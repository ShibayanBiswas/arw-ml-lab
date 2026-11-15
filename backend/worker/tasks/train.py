"""q.train.cpu — supervised CV train (Phase 2 thin)."""

from __future__ import annotations

from typing import Any

import pandas as pd
from labcore.preprocess.recipe import RecipeSpec
from labcore.train.run import TrainConfig, run_supervised_cv

from backend.app.dataset_store import DATASET_STORE
from backend.app.experiment_store import EXPERIMENT_STORE
from backend.app.jobs_store import JOB_STORE
from backend.worker.celery_app import celery_app


@celery_app.task(name="lab.train.run", bind=True, queue="q.train.cpu")
def run_train_task(self, job_id: str, experiment_id: str, body: dict[str, Any]) -> dict[str, Any]:  # noqa: ANN001
    _ = self
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
        )
        JOB_STORE.update(
            job_id,
            progress=0.4,
            step="cv",
            event={"type": "progress", "pct": 0.4, "step": "cv"},
        )
        result = run_supervised_cv(df, cfg)
        EXPERIMENT_STORE.update(
            experiment_id,
            status="done",
            leaderboard=result["leaderboard"],
            result=result,
        )
        out = {"experiment_id": experiment_id, "n_models": len(result["leaderboard"])}
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
        EXPERIMENT_STORE.update(experiment_id, status="error")
        JOB_STORE.update(
            job_id,
            status="error",
            error=str(exc),
            event={"type": "error", "message": str(exc)},
        )
        raise
