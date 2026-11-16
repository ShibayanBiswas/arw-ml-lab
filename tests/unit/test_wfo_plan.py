"""WFO planner + retune loop tests (Phase 5A)."""

from __future__ import annotations

import numpy as np
from labcore.finance.wfo import plan_wfo_windows, run_wfo_regression


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


def test_wfo_regression_reports_real_oos_metrics():
    rng = np.random.default_rng(42)
    n = 240
    X = rng.normal(size=(n, 3))
    y = X @ np.array([0.5, -0.2, 0.8]) + rng.normal(0, 0.1, size=n)
    out = run_wfo_regression(
        X, y, n_windows=4, l_is=80, l_oos=20, step=20, gap=2, mode="expanding", seed=42
    )
    assert out["id"] == "WFO.T.REGRESSION"
    assert len(out["windows"]) >= 3
    assert np.isfinite(out["oos_r2_mean"])
    assert np.isfinite(out["oos_mae_mean"])
    # Signal is linear — mean OOS R² should be clearly positive
    assert out["oos_r2_mean"] > 0.5, out["oos_r2_mean"]
    for w in out["windows"]:
        assert "oos_r2" in w and "oos_mae" in w
