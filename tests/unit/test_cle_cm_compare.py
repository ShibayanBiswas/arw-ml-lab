"""CLE.P.CM_COST / CM_DELTA / COMPARE_BARS."""

from __future__ import annotations

import numpy as np
from labcore.eval.classification.plots import plot_cm_cost, plot_cm_delta, plot_compare_bars


def test_cm_cost_delta_compare():
    y = np.array([0, 0, 1, 1, 1, 0, 1, 0])
    pred_a = np.array([0, 1, 1, 1, 0, 0, 1, 0])
    pred_b = np.array([0, 0, 1, 0, 1, 0, 1, 1])
    cost = np.array([[0.0, 1.0], [2.0, 0.0]])
    c = plot_cm_cost(y, pred_a, cost, labels=[0, 1])
    assert c["id"] == "CLE.P.CM_COST"
    assert c["numbers"]["total_cost"] >= 0
    d = plot_cm_delta(y, pred_a, pred_b, labels=[0, 1])
    assert d["id"] == "CLE.P.CM_DELTA"
    bars = plot_compare_bars(
        {"a": 0.8, "b": 0.75},
        cis={"a": (0.7, 0.9), "b": (0.65, 0.85)},
        metric="f1",
    )
    assert bars["id"] == "CLE.P.COMPARE_BARS"
