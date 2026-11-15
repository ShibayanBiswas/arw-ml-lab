"""Phase 0 dummy job — streams progress for JobProgress / SSE AC."""

from __future__ import annotations

import time

from backend.app.jobs_store import JOB_STORE
from backend.worker.celery_app import celery_app


@celery_app.task(name="lab.demo.progress", bind=True, queue="q.demo")
def run_demo_progress(self, job_id: str) -> dict[str, float]:  # noqa: ANN001
    _ = self
    steps = [
        (0.2, "prepare"),
        (0.45, "compute"),
        (0.7, "aggregate"),
        (0.9, "finalise"),
        (1.0, "done"),
    ]
    JOB_STORE.update(
        job_id,
        status="running",
        progress=0.05,
        step="start",
        event={"type": "progress", "pct": 0.05, "step": "start"},
    )
    for pct, step in steps:
        time.sleep(0.25)
        if pct < 1.0:
            JOB_STORE.update(
                job_id,
                status="running",
                progress=pct,
                step=step,
                event={"type": "progress", "pct": pct, "step": step},
            )
        else:
            result = {"seed": 42, "ok": True}
            JOB_STORE.update(
                job_id,
                status="done",
                progress=1.0,
                step=step,
                result=result,
                event={"type": "done", "pct": 1.0, "result": result},
            )
    return {"job_id": job_id, "progress": 1.0}
