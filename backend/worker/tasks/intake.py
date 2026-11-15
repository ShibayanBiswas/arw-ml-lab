"""q.eda — run intake detectors after ingest."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from labcore.intake.pipeline import run_intake

from backend.app.dataset_store import DATASET_STORE
from backend.app.intake_store import INTAKE_STORE
from backend.app.jobs_store import JOB_STORE
from backend.worker.celery_app import celery_app


@celery_app.task(name="lab.intake.run", bind=True, queue="q.eda")
def run_intake_task(
    self,  # noqa: ANN001
    job_id: str,
    dataset_version_id: str,
    *,
    parent_version_id: str | None = None,
    use_llm: bool = False,
) -> dict[str, str]:
    _ = self
    _ = use_llm  # Phase 6
    JOB_STORE.update(
        job_id,
        status="running",
        progress=0.1,
        step="intake",
        event={"type": "progress", "pct": 0.1, "step": "intake"},
    )
    try:
        ds = DATASET_STORE.get(dataset_version_id)
        if ds is None or not ds.parquet_path:
            raise ValueError("dataset version or parquet missing")
        df = pd.read_parquet(ds.parquet_path)
        parent_df = None
        if parent_version_id:
            parent = DATASET_STORE.get(parent_version_id)
            if parent and parent.parquet_path and Path(parent.parquet_path).exists():
                parent_df = pd.read_parquet(parent.parquet_path)

        result = run_intake(df, parent_df=parent_df, dataset_name=ds.name)
        rec = INTAKE_STORE.save_proposal(
            workspace_id=ds.workspace_id,
            dataset_version_id=dataset_version_id,
            rules_version=result["rules_version"],
            detector_output=result["detector_output"],
            llm_output=result["llm_output"],
            merged=result["merged"],
            validator_report=result["validator_report"],
            confidence_overall=float(result.get("confidence_overall") or 0.0),
            versioning=result.get("versioning"),
            status="proposed",
        )
        if result.get("versioning"):
            INTAKE_STORE.save_diff(
                f"{dataset_version_id}:{parent_version_id}",
                result["versioning"],
            )
        # Do not overwrite Phase-1 TaskSpec on the dataset; intake proposal lives in INTAKE_STORE.
        # Confirmed task_spec attaches to the experiment via the confirm endpoint.
        out = {
            "proposal_id": rec.id,
            "dataset_version_id": dataset_version_id,
            "confidence_overall": str(rec.confidence_overall),
        }
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
        JOB_STORE.update(
            job_id,
            status="error",
            error=str(exc),
            event={"type": "error", "message": str(exc)},
        )
        raise
