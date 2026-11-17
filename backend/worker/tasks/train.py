"""q.train.cpu — supervised CV train (Phase 2 thin)."""

from __future__ import annotations

from typing import Any

import pandas as pd
from labcore.ops.soft_time_limit import is_soft_time_limit_exc, save_best_so_far
from labcore.preprocess.recipe import RecipeSpec
from labcore.train.run import TrainConfig, run_supervised_cv

from backend.app.dataset_store import DATASET_STORE
from backend.app.experiment_store import EXPERIMENT_STORE
from backend.app.jobs_store import JOB_STORE
from backend.worker.celery_app import celery_app


@celery_app.task(name="lab.train.run", bind=True, queue="q.train.cpu")
def run_train_task(self, job_id: str, experiment_id: str, body: dict[str, Any]) -> dict[str, Any]:  # noqa: ANN001
    _ = self
    partial: dict[str, Any] | None = None
    JOB_STORE.update(
        job_id,
        status="running",
        progress=0.1,
        step="load",
        event={"type": "progress", "pct": 0.1, "step": "load"},
    )
    try:
        ds = DATASET_STORE.get(body["dataset_id"])
        if ds is None or not ds.parquet_path:
            raise FileNotFoundError("dataset parquet missing")
        df = pd.read_parquet(ds.parquet_path)
        EXPERIMENT_STORE.update(experiment_id, status="running")
        cfg = TrainConfig(
            task=body.get("task", "binary"),  # type: ignore[arg-type]
            target=body["target"],
            algorithm_keys=list(body.get("algorithm_keys") or []),
            n_splits=int(body.get("n_splits") or 5),
            seed=42,
            recipe=RecipeSpec(seed=42),
            cv_scheme=body.get("cv_scheme"),
            dataset_id=str(body.get("dataset_id") or body.get("sample_id") or "unknown"),
            workspace_id=str(body.get("workspace_id") or "offline"),
            refit_full=bool(body.get("refit_full", True)),
        )
        JOB_STORE.update(
            job_id,
            progress=0.4,
            step="cv",
            event={"type": "progress", "pct": 0.4, "step": "cv"},
        )
        result = run_supervised_cv(df, cfg)
        # MI-16: best-effort audit_log write when Postgres is reachable (oneshot-c225)
        try:
            from labcore.integrity.holdout_reuse import persist_holdout_audit_row

            hr = result.get("holdout_reuse") or {}
            audit_row = hr.get("audit_row")
            if isinstance(audit_row, dict):
                from backend.worker.maintenance import _connect_postgres

                conn = _connect_postgres()
                if conn is not None:
                    try:
                        persist_meta = persist_holdout_audit_row(audit_row, execute=conn.execute)
                        hr["audit_persist"] = persist_meta
                        result["holdout_reuse"] = hr
                    finally:
                        conn.close()
        except Exception:  # noqa: BLE001 — never fail the train job on audit I/O
            pass
        # Persist champion pipeline for Prediction Studio (never pickle into experiment JSON)
        pipeline = result.pop("champion_pipeline", None)
        model_id = None
        if pipeline is not None:
            from backend.app.model_store import MODEL_STORE

            stored = MODEL_STORE.create(
                task=cfg.task,
                target=cfg.target,
                dataset_id=cfg.dataset_id,
                feature_names=list(result.get("feature_names") or []),
                feature_contract=dict(result.get("feature_contract") or {}),
                pipeline=pipeline,
                meta={
                    "experiment_id": experiment_id,
                    "algorithm_key": (result.get("champion") or {}).get("algorithm_key"),
                    "seed": 42,
                },
            )
            model_id = stored.id
            result["model_id"] = model_id
            if result.get("feature_contract") is not None:
                result["feature_contract"]["model_id"] = model_id
        EXPERIMENT_STORE.update(
            experiment_id,
            status="done",
            leaderboard=result["leaderboard"],
            result=result,
        )
        out = {
            "experiment_id": experiment_id,
            "n_models": len(result["leaderboard"]),
            "model_id": model_id,
        }
        partial = {**result, **out}
        JOB_STORE.update(
            job_id,
            status="done",
            progress=1.0,
            step="done",
            result=out,
            event={"type": "done", "pct": 1.0, "result": out},
        )
        return out
    except Exception as exc:
        if is_soft_time_limit_exc(exc):
            return save_best_so_far(
                job_update=JOB_STORE.update,
                experiment_update=EXPERIMENT_STORE.update,
                job_id=job_id,
                experiment_id=experiment_id,
                partial=partial,
                seed=42,
            )
        EXPERIMENT_STORE.update(experiment_id, status="error")
        JOB_STORE.update(
            job_id,
            status="error",
            error=str(exc),
            event={"type": "error", "message": str(exc)},
        )
        raise
