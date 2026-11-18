"""q.eda — run EDA tables/plots + rule insights."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from labcore.data.infer import ColumnProfile
from labcore.data.task_detect import TaskSpec
from labcore.eda.run import run_eda
from labcore.insights.rules import run_eda_rules
from labcore.observability.json_logging import bind_context, clear_context
from labcore.ops.soft_time_limit import (
    PartialHolder,
    is_soft_time_limit_exc,
    save_best_so_far,
)

from backend.app.dataset_store import DATASET_STORE
from backend.app.jobs_store import JOB_STORE
from backend.worker.celery_app import celery_app


@celery_app.task(name="lab.eda.run", bind=True, queue="q.eda")
def run_eda_task(self, job_id: str, eda_run_id: str, dataset_id: str) -> dict[str, object]:  # noqa: ANN001
    _ = self
    holder = PartialHolder()
    bind_context(job_id=job_id, run_id=eda_run_id, workspace_id="eda")
    JOB_STORE.update(
        job_id,
        status="running",
        progress=0.1,
        step="load",
        event={"type": "progress", "pct": 0.1, "step": "load"},
    )
    try:
        ds = DATASET_STORE.get(dataset_id)
        if ds is None or not ds.parquet_path:
            raise FileNotFoundError(f"dataset {dataset_id} missing parquet")
        df = pd.read_parquet(ds.parquet_path)
        schema = [ColumnProfile.model_validate(c) for c in ds.schema] if ds.schema else None
        task = TaskSpec.model_validate(ds.task) if ds.task else None
        holder.update({"dataset_id": dataset_id, "eda_run_id": eda_run_id, "n_rows": int(len(df))})
        JOB_STORE.update(
            job_id,
            progress=0.35,
            step="eda",
            event={"type": "progress", "pct": 0.35, "step": "eda"},
        )
        result = run_eda(df, schema=schema, task=task, seed=42, render_png=False)
        insights = run_eda_rules(df, result.schema, result.task)
        # Persist artefacts without huge plotly blobs in job result — keep summary + full in store
        slim = []
        for a in result.artefacts:
            d = a.model_dump()
            # Drop png_b64 from API payload size; keep plotly for UI
            if d.get("png_b64") and len(d["png_b64"]) > 1000:
                d["png_b64"] = None
                d["png_uri"] = f"inline:{a.id}"
            slim.append(d)
        summary = {
            "eda_run_id": eda_run_id,
            "dataset_id": dataset_id,
            "table_ids": result.table_ids,
            "plot_ids": result.plot_ids,
            "plot_groups": result.plot_groups,
            "n_artefacts": len(result.artefacts),
            "sampled": result.sampled,
            "n_insights": len(insights),
            "task": result.task.model_dump(),
        }
        holder.update(summary)
        DATASET_STORE.update_eda(
            eda_run_id,
            status="done",
            result_summary=summary,
            artefacts=slim,
            insights=[i.model_dump() for i in insights],
        )
        JOB_STORE.update(
            job_id,
            status="done",
            progress=1.0,
            step="done",
            result=summary,
            event={"type": "done", "pct": 1.0, "result": summary},
        )
        return summary
    except Exception as exc:
        if is_soft_time_limit_exc(exc):
            return save_best_so_far(
                job_update=JOB_STORE.update,
                experiment_update=None,
                job_id=job_id,
                experiment_id=None,
                partial=holder.value,
                seed=42,
            )
        DATASET_STORE.update_eda(eda_run_id, status="error")
        JOB_STORE.update(
            job_id,
            status="error",
            error=str(exc),
            event={"type": "error", "message": str(exc)},
        )
        raise
    finally:
        clear_context()


_ = Path
