"""Per-queue soft/hard Celery time limits — OPS-03 / ARCHITECTURE §39.3 + §46.2.

Values are minutes in the architecture tables; this module exposes seconds for
Celery ``soft_time_limit`` / ``time_limit``. Soft → SoftTimeLimitExceeded so
tasks can save best-so-far; hard → kill.
"""

from __future__ import annotations

from typing import TypedDict

ARTEFACT_ID = "OPS.QUEUE.TIME_LIMITS"
STRESS_ID = "ST-OPS-03"


class QueueLimits(TypedDict):
    soft_s: int
    hard_s: int


# Minutes from §39.3 / OPS-03 → seconds
_QUEUE_LIMITS_MIN: dict[str, tuple[int, int]] = {
    "q.ingest": (10, 15),
    "q.eda": (15, 20),
    "q.train.cpu": (90, 120),
    "q.train.gpu": (90, 120),  # same wall-clock as CPU when GPU worker present
    "q.tune": (4 * 60, 5 * 60),
    "q.explain": (30, 40),
    "q.forecast": (60, 90),
    "q.insights": (5, 6),
    "q.report": (10, 15),
    "q.predict.batch": (30, 45),
    "q.predict.heavy": (60, 90),
    "q.demo": (5, 6),
}


def queue_time_limits_seconds() -> dict[str, QueueLimits]:
    return {
        q: {"soft_s": soft * 60, "hard_s": hard * 60}
        for q, (soft, hard) in _QUEUE_LIMITS_MIN.items()
    }


def celery_task_annotations() -> dict[str, dict[str, int]]:
    """Map Celery task names → soft/hard limits (matched to task_routes queues)."""
    limits = queue_time_limits_seconds()
    # task name → queue (must stay aligned with backend.worker.celery_app)
    task_queue = {
        "lab.demo.progress": "q.demo",
        "lab.ingest.parse": "q.ingest",
        "lab.ingest.sample": "q.ingest",
        "lab.eda.run": "q.eda",
        "lab.train.run": "q.train.cpu",
        "lab.tune.run": "q.tune",
        "lab.predict.batch": "q.predict.batch",
    }
    out: dict[str, dict[str, int]] = {}
    for task, queue in task_queue.items():
        lim = limits[queue]
        out[task] = {
            "soft_time_limit": lim["soft_s"],
            "time_limit": lim["hard_s"],
        }
    return out


def assert_hard_gt_soft(limits: dict[str, QueueLimits] | None = None) -> None:
    for q, lim in (limits or queue_time_limits_seconds()).items():
        if lim["hard_s"] <= lim["soft_s"]:
            raise ValueError(f"{q}: hard must exceed soft ({lim})")


def visibility_timeout_floor_s() -> int:
    """Broker visibility_timeout must exceed the max hard limit (OPS-04)."""
    return max(lim["hard_s"] for lim in queue_time_limits_seconds().values()) + 60
