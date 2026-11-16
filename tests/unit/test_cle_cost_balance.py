"""CLE.P.COST_CURVE + CLE.P.CLASS_BALANCE."""

from __future__ import annotations

import numpy as np
from labcore.eval.classification.plots import plot_class_balance, plot_cost_curve


def test_cost_curve_and_class_balance():
    rng = np.random.default_rng(42)
    y = np.r_[np.zeros(40, dtype=int), np.ones(60, dtype=int)]
    scores = np.clip(y.astype(float) + rng.normal(0, 0.3, size=y.shape), 0, 1)
    cost = plot_cost_curve(y, scores, c_fp=1.0, c_fn=2.0)
    assert cost["id"] == "CLE.P.COST_CURVE"
    assert "plotly" in cost
    assert np.isfinite(cost["numbers"]["best_cost"])

    bal = plot_class_balance({"0": 40, "1": 60}, {"0": 50, "1": 50})
    assert bal["id"] == "CLE.P.CLASS_BALANCE"
    assert "plotly" in bal
