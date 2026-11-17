"""OPS.QUEUE.TIME_LIMITS — Celery soft/hard limits (oneshot-c184)."""

from __future__ import annotations

from labcore.ops.queue_time_limits import visibility_timeout_floor_s
from labcore.ops.queue_time_limits_contract import (
    ARTEFACT_ID,
    STRESS_ID,
    queue_time_limits_manifest,
)


def test_queue_time_limits_manifest_seed_42() -> None:
    m = queue_time_limits_manifest(seed=42)
    assert m["id"] == ARTEFACT_ID
    assert m["stress_test"] == STRESS_ID
    assert m["seed"] == 42
    assert m["limits"]["q.tune"]["hard_s"] == 5 * 3600
    assert len(m["checks"]) == 2


def test_visibility_timeout_exceeds_tune_hard() -> None:
    assert visibility_timeout_floor_s() > 5 * 3600


def test_celery_app_imports_with_annotations() -> None:
    from backend.worker.celery_app import celery_app

    ann = celery_app.conf.task_annotations
    assert isinstance(ann, dict)
    assert ann["lab.eda.run"]["soft_time_limit"] == 15 * 60
    assert celery_app.conf.broker_transport_options["visibility_timeout"] >= visibility_timeout_floor_s()
