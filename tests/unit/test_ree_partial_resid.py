"""REE.P.PARTIAL_RESID — CCPR vs statsmodels plot_ccpr numbers."""

from __future__ import annotations

import numpy as np
import statsmodels.api as sm
from labcore.eval.regression.plots import plot_partial_resid
from statsmodels.tools.tools import add_constant


def test_partial_resid_matches_plot_ccpr_math():
    rng = np.random.default_rng(42)
    n = 80
    x0 = rng.uniform(0, 10, n)
    x1 = rng.normal(5, 2, n)
    y = 1.2 * x0 + 0.4 * x1 + rng.normal(0, 0.5, n)
    X = np.column_stack([x0, x1])
    names = ["feat_a", "feat_b"]

    exog = add_constant(X)
    ols = sm.OLS(y, exog).fit()
    art = plot_partial_resid(y, X, feature_names=names)
    assert art["id"] == "REE.P.PARTIAL_RESID"
    assert art["numbers"]["features_shown"] == 2
    assert len(art["plotly"]["data"]) >= 4

    for j, name in enumerate(names):
        exog_idx = j + 1
        x1 = exog[:, exog_idx]
        x1beta = x1 * ols.params[exog_idx]
        expected_partial = x1beta + ols.resid
        comp = sm.OLS(x1beta, add_constant(x1)).fit()

        nums = art["numbers"]["by_feature"][name]
        np.testing.assert_allclose(nums["partial_y"], expected_partial, rtol=0, atol=1e-12)
        np.testing.assert_allclose(nums["beta"], ols.params[exog_idx], rtol=0, atol=1e-12)
        np.testing.assert_allclose(nums["component_intercept"], comp.params[0], rtol=0, atol=1e-12)
        np.testing.assert_allclose(nums["component_slope"], comp.params[1], rtol=0, atol=1e-12)