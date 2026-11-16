"""F21 VAR multivariate forecaster + REE.P.CALIBRATION_BINS."""

from __future__ import annotations

import numpy as np
from labcore.eval.regression.plots import plot_calibration_bins
from labcore.timeseries.models import TS_MODEL_CATALOGUE, forecast


def test_var_forecast():
    assert any(m["id"] == "var" for m in TS_MODEL_CATALOGUE)
    rng = np.random.default_rng(42)
    n = 200
    x = rng.normal(0, 1, n).cumsum()
    y = 0.5 * x + rng.normal(0, 1, n)
    Y = np.c_[x, y]
    h = 8
    out = forecast("var", Y, h)
    assert out["y_pred"].shape == (h, 2)
    assert np.isfinite(out["y_pred"]).all()
    assert out["extra"]["lag_order"] >= 1


def test_ree_calibration_bins():
    rng = np.random.default_rng(42)
    y = rng.normal(10, 2, 100)
    pred = y + rng.normal(0, 0.5, 100)
    art = plot_calibration_bins(y, pred, n_bins=10)
    assert art["id"] == "REE.P.CALIBRATION_BINS"
    assert len(art["numbers"]["mean_pred"]) == 10
