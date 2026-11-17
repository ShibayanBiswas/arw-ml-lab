"""Experiments + leaderboard — Phase 2 thin."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse, Response
from labcore.train.export import leaderboard_to_csv, leaderboard_to_xlsx_bytes
from pydantic import BaseModel, Field

from backend.app.dataset_store import DATASET_STORE
from backend.app.experiment_store import EXPERIMENT_STORE
from backend.app.jobs_store import JOB_STORE
from backend.app.security import AuthUser, require_write_role
from backend.worker.tasks.train import run_train_task
from backend.worker.tasks.tune import run_tune_task

router = APIRouter(tags=["experiments"])


class TrainBody(BaseModel):
    dataset_id: str
    target: str
    task: str = "binary"
    algorithm_keys: list[str] = Field(default_factory=list)
    name: str | None = None
    n_splits: int = 5
    cv_scheme: str | None = None
    tuning_preset: str | None = None
    refit_full: bool = True  # ST-FEAT-02 — prepare-for-deployment (default ON)


class TuneBody(BaseModel):
    dataset_id: str
    target: str
    algorithm_key: str
    task: str = "binary"
    preset: str = "quick"
    n_splits: int = 5
    name: str | None = None
    fixed_params: dict[str, Any] | None = None
    n_trials: int | None = None
    refit_full: bool = True


def _reject_gpu_or_hidden(algorithm_keys: list[str]) -> None:
    """HTTP 422 when GPU-only model has no worker, or TabPFN requested while disabled."""
    from labcore.deep.gpu_guard_contract import validate_train_gpu_guard
    from labcore.deep.guards import tabpfn_enabled
    from labcore.registry.algorithms import thin_algorithm_specs

    by_key = {s.key: s for s in thin_algorithm_specs()}
    for key in algorithm_keys:
        spec = by_key.get(key)
        if spec is None:
            continue
        if spec.enabled_env == "TABPFN_ENABLED" and not tabpfn_enabled():
            raise HTTPException(
                status_code=422,
                detail="TabPFN is disabled (TABPFN_ENABLED=false); commercial licence required.",
            )
    try:
        validate_train_gpu_guard(algorithm_keys)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


def _dataset_shape(ds: Any) -> tuple[int, int]:
    """Best-effort (n_rows, n_cols) for MI-09 memory guard."""
    n_cols = len(ds.schema) if ds.schema else int(ds.meta.get("n_cols") or 0)
    n_rows = int(ds.meta.get("n_rows") or ds.meta.get("rows") or 0)
    if (n_rows <= 0 or n_cols <= 0) and ds.parquet_path:
        try:
            import pyarrow.parquet as pq

            pf = pq.ParquetFile(ds.parquet_path)
            n_rows = int(pf.metadata.num_rows) if n_rows <= 0 else n_rows
            n_cols = int(pf.metadata.num_columns) if n_cols <= 0 else n_cols
        except Exception:
            pass
    return max(n_rows, 0), max(n_cols, 0)


def _reject_memory_overflow(ds: Any) -> None:
    from labcore.ops.memory_enqueue import guard_train_enqueue

    n_rows, n_cols = _dataset_shape(ds)
    if n_rows <= 0 or n_cols <= 0:
        return
    decision = guard_train_enqueue(n_rows=n_rows, n_cols=n_cols)
    if decision.get("refused"):
        raise HTTPException(status_code=422, detail=decision["message"])


def _reject_max_rows(ds: Any) -> None:
    from backend.app.settings import get_settings
    from labcore.ops.max_rows_guard import guard_max_rows

    n_rows, _n_cols = _dataset_shape(ds)
    if n_rows <= 0:
        return
    decision = guard_max_rows(n_rows=n_rows, lab_max_rows=get_settings().lab_max_rows)
    if decision.get("refused"):
        raise HTTPException(status_code=422, detail=decision["message"])


@router.post("/api/v1/experiments/train")
def start_train(body: TrainBody, user: AuthUser = Depends(require_write_role)) -> dict[str, str]:
    ds = DATASET_STORE.get(body.dataset_id)
    if ds is None:
        raise HTTPException(status_code=404, detail="dataset not found")
    _reject_gpu_or_hidden(body.algorithm_keys)
    _reject_max_rows(ds)
    _reject_memory_overflow(ds)
    exp = EXPERIMENT_STORE.create(
        workspace_id=user.workspace_id or ds.workspace_id,
        dataset_id=body.dataset_id,
        name=body.name or f"train-{body.target}",
        family="supervised",
        task_spec=body.model_dump(),
        status="queued",
    )
    job = JOB_STORE.create(
        workspace_id=user.workspace_id or ds.workspace_id,
        kind="train",
        queue="q.train.cpu",
    )
    run_train_task.apply_async(args=(job.id, exp.id, body.model_dump()), queue="q.train.cpu")
    return {"job_id": job.id, "experiment_id": exp.id}


@router.post("/api/v1/experiments/tune")
def start_tune(body: TuneBody, user: AuthUser = Depends(require_write_role)) -> dict[str, str]:
    ds = DATASET_STORE.get(body.dataset_id)
    if ds is None:
        raise HTTPException(status_code=404, detail="dataset not found")
    _reject_gpu_or_hidden([body.algorithm_key])
    _reject_max_rows(ds)
    _reject_memory_overflow(ds)
    exp = EXPERIMENT_STORE.create(
        workspace_id=user.workspace_id or ds.workspace_id,
        dataset_id=body.dataset_id,
        name=body.name or f"tune-{body.algorithm_key}",
        family="supervised",
        task_spec=body.model_dump(),
        status="queued",
    )
    job = JOB_STORE.create(
        workspace_id=user.workspace_id or ds.workspace_id,
        kind="tune",
        queue="q.tune",
    )
    run_tune_task.apply_async(args=(job.id, exp.id, body.model_dump()), queue="q.tune")
    return {"job_id": job.id, "experiment_id": exp.id}


@router.get("/api/v1/experiments/{experiment_id}")
def get_experiment(
    experiment_id: str,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    rec = EXPERIMENT_STORE.get(experiment_id)
    if rec is None or rec.workspace_id != (user.workspace_id or rec.workspace_id):
        raise HTTPException(status_code=404, detail="experiment not found")
    result = rec.result or {}
    return {
        "id": rec.id,
        "name": rec.name,
        "status": rec.status,
        "task_spec": rec.task_spec,
        "leaderboard": rec.leaderboard,
        "result": result,
        "eval": result.get("eval"),
        "champion": result.get("champion"),
    }


@router.get("/api/v1/experiments/{experiment_id}/leaderboard")
def get_leaderboard(
    experiment_id: str,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    rec = EXPERIMENT_STORE.get(experiment_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="experiment not found")
    return {"experiment_id": experiment_id, "rows": rec.leaderboard}


@router.get("/api/v1/experiments/{experiment_id}/leaderboard.csv")
def export_leaderboard_csv(
    experiment_id: str,
    user: AuthUser = Depends(require_write_role),
) -> PlainTextResponse:
    rec = EXPERIMENT_STORE.get(experiment_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="experiment not found")
    body = leaderboard_to_csv(list(rec.leaderboard or []))
    return PlainTextResponse(
        body,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="leaderboard-{experiment_id}.csv"'},
    )


@router.get("/api/v1/experiments/{experiment_id}/leaderboard.xlsx")
def export_leaderboard_xlsx(
    experiment_id: str,
    user: AuthUser = Depends(require_write_role),
) -> Response:
    rec = EXPERIMENT_STORE.get(experiment_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="experiment not found")
    body = leaderboard_to_xlsx_bytes(list(rec.leaderboard or []))
    return Response(
        content=body,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="leaderboard-{experiment_id}.xlsx"'},
    )
