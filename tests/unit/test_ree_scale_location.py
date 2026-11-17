"""REE.P.SCALE_LOCATION — scale-location with statsmodels LOWESS."""

from __future__ import annotations

import numpy as np
from labcore.eval.regression.plots import plot_scale_location
from statsmodels.nonparametric.smoothers_lowess import lowess


def test_scale_location_lowess_matches_statsmodels():
    rng = np.random.default_rng(42)
    y_pred = rng.uniform(1.0, 20.0, 88)
    resid = rng.normal(0.0, 1.2, 88) + 0.05 * (y_pred - 10.0) ** 2
    frac = 0.5
    art = plot_scale_location(y_pred, resid, frac=frac)
    assert art["id"] == "REE.P.SCALE_LOCATION"
    assert art["plotly"]["data"]

    sd = float(np.nanstd(resid, ddof=1))
    scale = np.sqrt(np.abs(resid / sd))
    sm = lowess(scale, y_pred, frac=frac, return_sorted=True)
    np.testing.assert_allclose(art["numbers"]["residual_sd"], sd, rtol=0, atol=1e-12)
    np.testing.assert_allclose(art["numbers"]["lowess_x"], sm[:, 0], rtol=0, atol=1e-12)
    np.testing.assert_allclose(art["numbers"]["lowess_y"], sm[:, 1], rtol=0, atol=1e-12)