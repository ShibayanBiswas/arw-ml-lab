"""F23 VECM multivariate cointegrated forecaster."""

from __future__ import annotations

import numpy as np
from labcore.timeseries.models import TS_MODEL_CATALOGUE, forecast


def test_vecm_forecast():
    assert any(m["id"] == "vecm" for m in TS_MODEL_CATALOGUE)
    rng = np.random.default_rng(42)
    n = 300
    e = rng.normal(0, 1, n).cumsum()
    x = e + rng.normal(0, 0.5, n)
    y = e + rng.normal(0, 0.5, n)
    Y = np.c_[x, y]
    h = 5
    out = forecast("vecm", Y, h)
    assert out["y_pred"].shape == (h, 2)
    assert np.isfinite(out["y_pred"]).all()
    assert out["extra"]["coint_rank"] >= 1
