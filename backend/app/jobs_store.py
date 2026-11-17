"""In-memory job status for Phase 0 SSE demo (Redis-backed Celery; status mirrored here)."""

from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Literal

JobState = Literal["queued", "running", "done", "error", "cancelled"]


@dataclass
class JobRecord:
    job_id: str
    status: JobState = "queued"
    progress: float = 0.0
    step: str | None = None
    result: dict[str, Any] | None = None
    error: str | None = None
    events: list[dict[str, Any]] = field(default_factory=list)
    idempotency_key: str | None = None
    created_at: float = field(default_factory=time.time)
    heartbeat_at: float | None = None


class JobStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._jobs: dict[str, JobRecord] = {}
        self._by_idempotency: dict[str, str] = {}

    def create(self, *, idempotency_key: str | None = None) -> JobRecord:
        with self._lock:
            if idempotency_key and idempotency_key in self._by_idempotency:
                return self._jobs[self._by_idempotency[idempotency_key]]
            job_id = str(uuid.uuid4())
            rec = JobRecord(job_id=job_id, idempotency_key=idempotency_key)
            rec.events.append({"type": "progress", "pct": 0.0, "step": "queued"})
            self._jobs[job_id] = rec
            if idempotency_key:
                self._by_idempotency[idempotency_key] = job_id
            return rec

    def get(self, job_id: str) -> JobRecord | None:
        with self._lock:
            return self._jobs.get(job_id)

    def update(
        self,
        job_id: str,
        *,
        status: JobState | None = None,
        progress: float | None = None,
        step: str | None = None,
        result: dict[str, Any] | None = None,
        error: str | None = None,
        event: dict[str, Any] | None = None,
    ) -> JobRecord | None:
        with self._lock:
            rec = self._jobs.get(job_id)
            if rec is None:
                return None
            if status is not None:
                rec.status = status
            if progress is not None:
                rec.progress = progress
            if step is not None:
                rec.step = step
            if result is not None:
                rec.result = result
            if error is not None:
                rec.error = error
            if event is not None:
                rec.events.append(event)
            if status == "running" or (progress is not None and progress > 0):
                rec.heartbeat_at = time.time()
            return rec


JOB_STORE = JobStore()
