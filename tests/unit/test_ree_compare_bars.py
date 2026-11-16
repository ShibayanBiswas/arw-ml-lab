"""REE.P.COMPARE_BARS."""

from __future__ import annotations

from labcore.eval.regression.plots import plot_compare_bars_ree


def test_ree_compare_bars():
    art = plot_compare_bars_ree(
        {"ridge": 1.2, "rf": 0.9},
        cis={"ridge": (1.0, 1.4), "rf": (0.7, 1.1)},
        metric="rmse",
    )
    assert art["id"] == "REE.P.COMPARE_BARS"
    assert art["numbers"]["scores"]["rf"] == 0.9
