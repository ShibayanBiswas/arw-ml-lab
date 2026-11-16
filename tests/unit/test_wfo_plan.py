"""WFO planner property tests (Phase 5A thin)."""

from __future__ import annotations

from labcore.finance.wfo import plan_wfo_windows


def test_expanding_windows_monotonic():
    plan = plan_wfo_windows(200, n_windows=5, l_is=60, l_oos=20, step=20, gap=2, mode="expanding")
    assert plan["n_windows"] >= 3
    prev_oos = -1
    for w in plan["windows"]:
        assert w["is_start"] == 0
        assert w["is_end"] <= w["oos_start"]
        assert w["oos_start"] >= prev_oos
        assert w["n_is"] > 0 and w["n_oos"] > 0
        prev_oos = w["oos_start"]


def test_rolling_bounded_is():
    plan = plan_wfo_windows(150, n_windows=4, l_is=40, l_oos=15, step=15, mode="rolling")
    for w in plan["windows"]:
        assert w["is_end"] - w["is_start"] <= 40 + 1
