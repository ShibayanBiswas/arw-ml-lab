"""Experiments + leaderboard — Phase 2 thin."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from labcore.train.export import leaderboard_to_csv
from pydantic import BaseModel, Field

from backend.app.dataset_store import DATASET_STORE
from backend.app.experiment_store import EXPERIMENT_STORE
from backend.app.jobs_store import JOB_STORE
from backend.app.security import AuthUser, require_write_role
from backend.worker.tasks.train import run_train_task

router = APIRouter(tags=["experiments"])


class TrainBody(BaseModel):
    dataset_id: str
    target: str
    task: str = "binary"
    algorithm_keys: list[str] = Field(default_factory=list)
    name: str | None = None
    n_splits: int = 5


@router.post("/api/v1/experiments/train")
def start_train(body: TrainBody, user: AuthUser = Depends(require_write_role)) -> dict[str, str]:
    ds = DATASET_STORE.get(body.dataset_id)
    if ds is None:
        raise HTTPException(status_code=404, detail="dataset not found")
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


@router.get("/api/v1/experiments/{experiment_id}")
def get_experiment(
    experiment_id: str,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    rec = EXPERIMENT_STORE.get(experiment_id)
    if rec is None or rec.workspace_id != (user.workspace_id or rec.workspace_id):
        raise HTTPException(status_code=404, detail="experiment not found")
    return {
        "id": rec.id,
        "name": rec.name,
        "status": rec.status,
        "task_spec": rec.task_spec,
        "leaderboard": rec.leaderboard,
        "result": rec.result,
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
        headers={
            "Content-Disposition": f'attachment; filename="leaderboard-{experiment_id}.csv"'
        },
    )
