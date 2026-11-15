"""q.ingest — parse upload → Parquet → schema + task."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from labcore.data.infer import infer_schema
from labcore.data.readers import dataframe_meta, normalise_columns, read_tabular, write_parquet
from labcore.data.task_detect import detect_task

from backend.app.dataset_store import DATASET_STORE
from backend.app.jobs_store import JOB_STORE
from backend.app.storage import get_storage
from backend.worker.celery_app import celery_app


@celery_app.task(name="lab.ingest.parse", bind=True, queue="q.ingest")
def ingest_dataset(
    self,  # noqa: ANN001
    job_id: str,
    dataset_id: str,
    *,
    storage_key: str | None = None,
    local_path: str | None = None,
    target: str | None = None,
    family_hint: str | None = None,
) -> dict[str, str]:
    _ = self
    JOB_STORE.update(
        job_id,
        status="running",
        progress=0.1,
        step="load",
        event={"type": "progress", "pct": 0.1, "step": "load"},
    )
    try:
        path: Path
        if local_path:
            path = Path(local_path)
        elif storage_key:
            storage = get_storage()
            lp = storage.local_path(storage_key)
            if lp is None:
                data = storage.get_bytes(storage_key)
                tmp = Path(".cache") / "uploads" / storage_key
                tmp.parent.mkdir(parents=True, exist_ok=True)
                tmp.write_bytes(data)
                path = tmp
            else:
                path = lp
        else:
            raise ValueError("storage_key or local_path required")

        df = read_tabular(path)
        df = normalise_columns(df)
        JOB_STORE.update(
            job_id,
            progress=0.4,
            step="infer",
            event={"type": "progress", "pct": 0.4, "step": "infer"},
        )
        schema = infer_schema(df)
        task = detect_task(
            df,
            schema,
            target=target if target and target in df.columns else None,
            family_hint=family_hint,
        )
        out_dir = Path(".cache") / "parquet"
        out_dir.mkdir(parents=True, exist_ok=True)
        pq = out_dir / f"{dataset_id}.parquet"
        digest = write_parquet(df, pq)
        DATASET_STORE.update(
            dataset_id,
            parquet_path=str(pq),
            content_hash=digest,
            schema=[c.model_dump() for c in schema],
            task=task.model_dump(),
            meta=dataframe_meta(df),
        )
        result = {
            "dataset_id": dataset_id,
            "content_hash": digest,
            "n_rows": str(len(df)),
            "n_cols": str(df.shape[1]),
            "task": task.task,
        }
        JOB_STORE.update(
            job_id,
            status="done",
            progress=1.0,
            step="done",
            result=result,
            event={"type": "done", "pct": 1.0, "result": result},
        )
        return result
    except Exception as exc:
        JOB_STORE.update(
            job_id,
            status="error",
            error=str(exc),
            event={"type": "error", "message": str(exc)},
        )
        raise


@celery_app.task(name="lab.ingest.sample", bind=True, queue="q.ingest")
def ingest_sample(self, job_id: str, dataset_id: str, sample_id: str) -> dict[str, str]:  # noqa: ANN001
    _ = self
    from labcore.data.samples import load_sample

    JOB_STORE.update(
        job_id,
        status="running",
        progress=0.2,
        step="load_sample",
        event={"type": "progress", "pct": 0.2, "step": "load_sample"},
    )
    try:
        payload = load_sample(sample_id)
        # Drop dataframe from store payload (keep path)
        DATASET_STORE.update(
            dataset_id,
            parquet_path=payload["path"],
            content_hash=payload["content_hash"],
            schema=payload["schema"],
            task=payload["task"],
            meta=payload["meta"],
            name=payload.get("name") or sample_id,
        )
        result = {
            "dataset_id": dataset_id,
            "sample_id": sample_id,
            "content_hash": payload["content_hash"],
            "n_rows": str(payload["meta"]["n_rows"]),
            "n_cols": str(payload["meta"]["n_cols"]),
        }
        JOB_STORE.update(
            job_id,
            status="done",
            progress=1.0,
            step="done",
            result=result,
            event={"type": "done", "pct": 1.0, "result": result},
        )
        return result
    except Exception as exc:
        JOB_STORE.update(
            job_id,
            status="error",
            error=str(exc),
            event={"type": "error", "message": str(exc)},
        )
        raise


# Ensure pandas is imported for type checkers / side effects
_ = pd
