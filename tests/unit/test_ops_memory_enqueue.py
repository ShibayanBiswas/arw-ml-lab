"""OPS.MEMORY.ENQUEUE — MI-09 train enqueue guard (oneshot-c192)."""

from __future__ import annotations

from labcore.ops.memory_enqueue import (
    ARTEFACT_ID,
    DEFAULT_WORKER_TRAIN_LIMIT_BYTES,
    guard_train_enqueue,
)


def test_guard_allows_small_frame() -> None:
    d = guard_train_enqueue(n_rows=1000, n_cols=20)
    assert d["artefact"] == ARTEFACT_ID
    assert d["refused"] is False
    assert d["allowed"] is True


def test_guard_refuses_huge_frame() -> None:
    # Force estimate well above 1.2 × Contabo 3584 MiB cap
    d = guard_train_enqueue(
        n_rows=50_000_000,
        n_cols=500,
        model_factor=4.0,
        worker_limit_bytes=DEFAULT_WORKER_TRAIN_LIMIT_BYTES,
    )
    assert d["refused"] is True
    assert "refuse:" in d["message"]


def test_router_wires_memory_guard() -> None:
    from pathlib import Path

    src = (Path(__file__).resolve().parents[2] / "backend/app/routers/experiments.py").read_text(
        encoding="utf-8"
    )
    assert "_reject_memory_overflow" in src
    assert "guard_train_enqueue" in src
