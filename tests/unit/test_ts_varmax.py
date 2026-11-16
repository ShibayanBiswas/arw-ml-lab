"""F22 VARMAX multivariate forecaster."""

from __future__ import annotations

import numpy as np
from labcore.timeseries.models import TS_MODEL_CATALOGUE, forecast


def test_varmax_forecast():
    assert any(m["id"] == "varmax" for m in TS_MODEL_CATALOGUE)
    rng = np.random.default_rng(42)
    Y = rng.normal(0, 1, (120, 2)).cumsum(axis=0)
    h = 5
    out = forecast("varmax", Y, h)
    assert out["y_pred"].shape == (h, 2)
    assert np.isfinite(out["y_pred"]).all()
