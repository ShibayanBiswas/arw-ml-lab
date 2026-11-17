"""REE.P.RESID_FITTED — residuals vs fitted with statsmodels LOWESS."""

from __future__ import annotations

import numpy as np
from labcore.eval.regression.plots import plot_resid_fitted
from statsmodels.nonparametric.smoothers_lowess import lowess


def test_resid_fitted_lowess_matches_statsmodels():
    rng = np.random.default_rng(42)
    y_pred = rng.uniform(2.0, 12.0, 96)
    resid = 0.08 * (y_pred - 7.0) + rng.normal(0.0, 0.45, 96)
    frac = 0.45
    art = plot_resid_fitted(y_pred, resid, frac=frac)
    assert art["id"] == "REE.P.RESID_FITTED"
    assert art["plotly"]["data"]

    sm = lowess(resid, y_pred, frac=frac, return_sorted=True)
    np.testing.assert_allclose(art["numbers"]["lowess_x"], sm[:, 0], rtol=0, atol=1e-12)
    np.testing.assert_allclose(art["numbers"]["lowess_y"], sm[:, 1], rtol=0, atol=1e-12)