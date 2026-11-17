"""OPS.WORKER.RECYCLE — oneshot-c197."""

from pathlib import Path

from labcore.ops.worker_recycle import (
    MAX_TASKS_PER_CHILD,
    STOP_GRACE_SECONDS,
    assert_worker_recycle_contract,
    celery_recycle_settings,
)


def test_worker_recycle_contract() -> None:
    out = assert_worker_recycle_contract()
    assert out["max_tasks"] == 20
    assert out["stop_grace_s"] == 300
    assert out["train_mib"] < 3584


def test_celery_app_has_max_tasks_per_child() -> None:
    from backend.worker.celery_app import celery_app

    assert celery_app.conf.worker_max_tasks_per_child == MAX_TASKS_PER_CHILD
    assert celery_app.conf.worker_max_memory_per_child is not None


def test_compose_stop_grace_300() -> None:
    text = Path("docker-compose.prod.yml").read_text(encoding="utf-8")
    assert f"stop_grace_period: {STOP_GRACE_SECONDS}s" in text
    assert text.count("--max-tasks-per-child") >= 2
    assert text.count("\n      - \"20\"") >= 2


def test_train_settings_contabo_budget() -> None:
    s = celery_recycle_settings("worker-train")
    assert s["worker_max_memory_per_child"] / 1024 < 3584
