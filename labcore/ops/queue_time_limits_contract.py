"""Offline artefact OPS.QUEUE.TIME_LIMITS — Celery soft/hard limits (§39.3)."""

from __future__ import annotations

from pathlib import Path

from labcore.ops.queue_time_limits import (
    ARTEFACT_ID,
    STRESS_ID,
    assert_hard_gt_soft,
    celery_task_annotations,
    queue_time_limits_seconds,
    visibility_timeout_floor_s,
)

ROOT = Path(__file__).resolve().parents[2]
CELERY_APP = ROOT / "backend" / "worker" / "celery_app.py"


class QueueTimeLimitsContractError(ValueError):
    """Raised when queue time-limit contract fails."""


def assert_architecture_minutes() -> dict[str, object]:
    lim = queue_time_limits_seconds()
    expected = {
        "q.eda": (15 * 60, 20 * 60),
        "q.train.cpu": (90 * 60, 120 * 60),
        "q.tune": (4 * 3600, 5 * 3600),
        "q.predict.heavy": (60 * 60, 90 * 60),
        "q.ingest": (10 * 60, 15 * 60),
    }
    for q, (soft, hard) in expected.items():
        if lim[q]["soft_s"] != soft or lim[q]["hard_s"] != hard:
            raise QueueTimeLimitsContractError(f"{q} mismatch: {lim[q]}")
    assert_hard_gt_soft(lim)
    return {"queues_checked": list(expected), "n_queues": len(lim)}


def assert_celery_app_wires_annotations() -> dict[str, object]:
    src = CELERY_APP.read_text(encoding="utf-8")
    for needle in (
        "celery_task_annotations",
        "task_annotations",
        "visibility_timeout",
        "visibility_timeout_floor_s",
    ):
        if needle not in src:
            raise QueueTimeLimitsContractError(f"celery_app missing {needle}")
    ann = celery_task_annotations()
    if "lab.train.run" not in ann:
        raise QueueTimeLimitsContractError("lab.train.run annotation missing")
    if ann["lab.train.run"]["soft_time_limit"] != 90 * 60:
        raise QueueTimeLimitsContractError("lab.train.run soft mismatch")
    floor = visibility_timeout_floor_s()
    max_hard = max(a["time_limit"] for a in ann.values())
    if floor <= max_hard:
        raise QueueTimeLimitsContractError("visibility_timeout must exceed max hard")
    return {
        "annotated_tasks": sorted(ann),
        "visibility_timeout_s": floor,
        "max_annotated_hard_s": max_hard,
    }


def assert_queue_time_limits_contract() -> list[dict[str, object]]:
    return [assert_architecture_minutes(), assert_celery_app_wires_annotations()]


def queue_time_limits_manifest(*, seed: int = 42) -> dict[str, object]:
    return {
        "id": ARTEFACT_ID,
        "stress_test": STRESS_ID,
        "seed": seed,
        "checks": assert_queue_time_limits_contract(),
        "limits": queue_time_limits_seconds(),
    }
