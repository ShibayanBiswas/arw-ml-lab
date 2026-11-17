"""OPS-03 — worker heartbeat writes to ``jobs.heartbeat_at`` every ~30 s (ARCHITECTURE §46.2)."""

from __future__ import annotations

import logging
import threading
import uuid
from typing import Any

from celery import signals

from backend.app.jobs_store import JOB_STORE

log = logging.getLogger("lab.heartbeat")

HEARTBEAT_INTERVAL_S = 30
HEARTBEAT_SEED = 42

_TOUCH_SQL = """
UPDATE public.jobs
SET heartbeat_at = now()
WHERE id = %s::uuid
  AND status IN ('queued', 'running')
"""

_lock = threading.Lock()
_active: dict[str, _HeartbeatLoop] = {}


class _HeartbeatLoop:
    def __init__(self, job_id: str) -> None:
        self.job_id = job_id
        self._stop = threading.Event()
        self._thread = threading.Thread(
            target=self._run,
            name=f"job-heartbeat-{job_id[:8]}",
            daemon=True,
        )

    def start(self) -> None:
        touch_job_heartbeat(self.job_id)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._thread.join(timeout=HEARTBEAT_INTERVAL_S + 5)

    def _run(self) -> None:
        while not self._stop.wait(HEARTBEAT_INTERVAL_S):
            touch_job_heartbeat(self.job_id)


def _parse_job_id(args: tuple[Any, ...] | None, kwargs: dict[str, Any] | None) -> str | None:
    if kwargs and isinstance(kwargs.get("job_id"), str):
        raw = kwargs["job_id"]
    elif args and isinstance(args[0], str):
        raw = args[0]
    else:
        return None
    try:
        uuid.UUID(raw)
    except ValueError:
        return None
    return raw


def touch_job_heartbeat(job_id: str) -> dict[str, str | bool]:
    """Bump in-memory demo store and Postgres when available."""
    JOB_STORE.touch_heartbeat(job_id)
    backend = "memory"
    wrote = False
    from backend.worker.maintenance import _connect_postgres

    conn = _connect_postgres()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(_TOUCH_SQL, (job_id,))
                wrote = cur.rowcount > 0  # type: ignore[attr-defined]
            backend = "postgres"
        except Exception as exc:  # noqa: BLE001
            log.warning("heartbeat postgres skip job=%s: %s", job_id, exc)
        finally:
            conn.close()
    return {"job_id": job_id, "backend": backend, "postgres_row": wrote}


def _start_heartbeat(job_id: str) -> None:
    with _lock:
        existing = _active.get(job_id)
        if existing is not None:
            return
        loop = _HeartbeatLoop(job_id)
        _active[job_id] = loop
        loop.start()


def _stop_heartbeat(job_id: str | None) -> None:
    if not job_id:
        return
    with _lock:
        loop = _active.pop(job_id, None)
    if loop is not None:
        loop.stop()
        touch_job_heartbeat(job_id)


@signals.task_prerun.connect
def _on_task_prerun(
    sender: object | None = None,
    task_id: str | None = None,
    task: object | None = None,
    args: tuple[Any, ...] | None = None,
    kwargs: dict[str, Any] | None = None,
    **kw: object,
) -> None:
    _ = (sender, task_id, task, kw)
    job_id = _parse_job_id(args, kwargs)
    if job_id:
        _start_heartbeat(job_id)


@signals.task_postrun.connect
def _on_task_postrun(
    sender: object | None = None,
    task_id: str | None = None,
    task: object | None = None,
    args: tuple[Any, ...] | None = None,
    kwargs: dict[str, Any] | None = None,
    retval: object = None,
    state: str | None = None,
    **kw: object,
) -> None:
    _ = (sender, task_id, task, retval, state, kw)
    _stop_heartbeat(_parse_job_id(args, kwargs))


@signals.task_failure.connect
def _on_task_failure(
    sender: object | None = None,
    task_id: str | None = None,
    exception: BaseException | None = None,
    args: tuple[Any, ...] | None = None,
    kwargs: dict[str, Any] | None = None,
    einfo: object = None,
    **kw: object,
) -> None:
    _ = (sender, task_id, exception, einfo, kw)
    _stop_heartbeat(_parse_job_id(args, kwargs))