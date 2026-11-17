"""q.tune — Optuna Quick/Balanced (Phase 2-cont-2)."""

from __future__ import annotations

from typing import Any

import pandas as pd
from labcore.ops.soft_time_limit import is_soft_time_limit_exc, save_best_so_far
from labcore.preprocess.recipe import RecipeSpec
from labcore.train.tune import run_optuna_tune

from backend.app.dataset_store import DATASET_STORE
from backend.app.experiment_store import EXPERIMENT_STORE
from backend.app.jobs_store import JOB_STORE
from backend.app.settings import get_settings
from backend.worker.celery_app import celery_app


@celery_app.task(name="lab.tune.run", bind=True, queue="q.tune")
def run_tune_task(self, job_id: str, experiment_id: str, body: dict[str, Any]) -> dict[str, Any]:  # noqa: ANN001
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
        JOB_STORE.update(
            job_id,
            progress=0.3,
            step="tune",
            event={"type": "progress", "pct": 0.3, "step": "tune"},
        )
        settings = get_settings()
        storage = body.get("storage") or (settings.optuna_storage_url or None)
        study_name = body.get("study_name") or f"exp-{experiment_id}"
        result = run_optuna_tune(
            df,
            target=body["target"],
            algorithm_key=body["algorithm_key"],
            task=body.get("task", "binary"),
            preset=body.get("preset", "quick"),
            n_splits=int(body.get("n_splits") or 5),
            seed=42,
            recipe=RecipeSpec(seed=42),
            fixed_params=body.get("fixed_params"),
            n_trials=body.get("n_trials"),
            storage=storage,
            study_name=study_name,
        )
        EXPERIMENT_STORE.update(
            experiment_id,
            status="done",
            result={"tune": result},
            leaderboard=[],
        )
        out = {
            "experiment_id": experiment_id,
            "best_value": result.get("best_value"),
            "best_params": result.get("best_params"),
        }
        partial = {**result, **out, "leaderboard": []}
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
