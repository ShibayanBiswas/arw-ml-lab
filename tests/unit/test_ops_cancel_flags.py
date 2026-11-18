"""OPS cancel flags — cooperative predict cancel (oneshot-c273)."""

from __future__ import annotations

from labcore.ops.cancel_flags import (
    MemoryCancelFlagStore,
    cancel_flag_key_for_job,
    default_cancel_store,
    set_cancel_store,
)


def test_memory_cancel_flag_roundtrip() -> None:
    store = MemoryCancelFlagStore()
    key = cancel_flag_key_for_job("job-42")
    assert not store.is_cancelled(key)
    store.set_cancelled(key)
    assert store.is_cancelled(key)
    store.clear(key)
    assert not store.is_cancelled(key)


def test_default_store_injection() -> None:
    mem = MemoryCancelFlagStore()
    set_cancel_store(mem)
    try:
        assert default_cancel_store() is mem
        k = cancel_flag_key_for_job("j1")
        default_cancel_store().set_cancelled(k)
        assert mem.is_cancelled(k)
    finally:
        set_cancel_store(None)


def test_predict_task_source_wires_cancel_and_soft() -> None:
    from pathlib import Path

    src = (Path(__file__).resolve().parents[2] / "backend/worker/tasks/predict.py").read_text(
        encoding="utf-8"
    )
    assert "default_cancel_store" in src
    assert "PartialHolder" in src
    assert "save_best_so_far" in src
