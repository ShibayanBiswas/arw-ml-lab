"""Jobs + SSE — ARCHITECTURE §6.2 / CURSOR_PROMPT §4.3."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status
from fastapi.responses import StreamingResponse

from backend.app.jobs_store import JOB_STORE
from backend.app.schemas import JobCreateResponse, JobStatus
from backend.app.security import AuthUser, get_current_user, require_write_role
from backend.worker.tasks.demo import run_demo_progress

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


@router.post("/demo", status_code=status.HTTP_202_ACCEPTED, response_model=JobCreateResponse)
def create_demo_job(
    response: Response,
    user: AuthUser = Depends(require_write_role),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> JobCreateResponse:
    """Enqueue a dummy Celery job that streams progress (Phase 0 AC)."""
    _ = user
    rec = JOB_STORE.create(idempotency_key=idempotency_key)
    try:
        run_demo_progress.delay(rec.job_id)
    except Exception:
        # Local/unit fallback when Redis broker is unavailable
        run_demo_progress.apply(args=(rec.job_id,))
    response.status_code = status.HTTP_202_ACCEPTED
    return JobCreateResponse(job_id=rec.job_id)


@router.get("/{job_id}", response_model=JobStatus)
def get_job(job_id: str, user: AuthUser = Depends(get_current_user)) -> JobStatus:
    _ = user
    rec = JOB_STORE.get(job_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatus(
        job_id=rec.job_id,
        status=rec.status,
        progress=rec.progress,
        step=rec.step,
        result=rec.result,
        error=rec.error,
    )


@router.get("/{job_id}/events")
async def job_events(
    job_id: str,
    request: Request,
    user: AuthUser = Depends(get_current_user),
) -> StreamingResponse:
    """SSE stream served by lab-api (not Vercel)."""
    _ = user
    rec = JOB_STORE.get(job_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="Job not found")

    async def event_gen() -> AsyncIterator[str]:
        cursor = 0
        while True:
            if await request.is_disconnected():
                break
            current = JOB_STORE.get(job_id)
            if current is None:
                yield f"event: error\ndata: {json.dumps({'message': 'missing'})}\n\n"
                break
            while cursor < len(current.events):
                evt = current.events[cursor]
                cursor += 1
                etype = evt.get("type", "message")
                yield f"event: {etype}\ndata: {json.dumps(evt)}\n\n"
                if etype in ("done", "error"):
                    return
            await asyncio.sleep(0.15)

    return StreamingResponse(event_gen(), media_type="text/event-stream")


@router.post("/{job_id}/cancel", status_code=status.HTTP_202_ACCEPTED)
def cancel_job(job_id: str, user: AuthUser = Depends(require_write_role)) -> dict[str, str]:
    _ = user
    rec = JOB_STORE.update(
        job_id,
        status="cancelled",
        event={"type": "error", "message": "cancelled"},
    )
    if rec is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job_id, "status": "cancelled"}
