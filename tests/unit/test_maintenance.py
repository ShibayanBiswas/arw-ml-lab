"""lab-beat maintenance CLI must exit 0 (Phase 8.1 stubs)."""

from __future__ import annotations

from backend.worker.maintenance import main, run_all


def test_run_all_returns_seed() -> None:
    out = run_all()
    assert out["seed"] == 42
    assert "reaper" in out


def test_main_all_exit_zero() -> None:
    assert main(["--all"]) == 0
