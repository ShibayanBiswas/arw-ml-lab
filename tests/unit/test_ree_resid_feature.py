"""REE.P.RESID_FEATURE — residuals vs features (LOWESS small multiples)."""

from __future__ import annotations

import numpy as np
from labcore.eval.regression.plots import plot_resid_feature
from statsmodels.nonparametric.smoothers_lowess import lowess


def test_resid_feature_lowess_matches_statsmodels():
    rng = np.random.default_rng(42)
    n = 80
    x0 = rng.uniform(0, 10, n)
    x1 = rng.normal(5, 2, n)
    resid = 0.15 * (x0 - 5) + rng.normal(0, 0.3, n)
    X = np.column_stack([x0, x1])
    frac = 0.4
    names = ["feat_a", "feat_b"]
    art = plot_resid_feature(resid, X, feature_names=names, frac=frac)
    assert art["id"] == "REE.P.RESID_FEATURE"
    assert art["numbers"]["features_shown"] == 2
    assert len(art["plotly"]["data"]) >= 4

    for name, col in zip(names, [x0, x1], strict=True):
        sm = lowess(resid, col, frac=frac, return_sorted=True)
        nums = art["numbers"]["by_feature"][name]
        np.testing.assert_allclose(nums["lowess_x"], sm[:, 0], rtol=0, atol=1e-12)
        np.testing.assert_allclose(nums["lowess_y"], sm[:, 1], rtol=0, atol=1e-12)