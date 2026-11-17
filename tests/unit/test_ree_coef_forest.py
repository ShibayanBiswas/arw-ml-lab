"""REE.P.COEF_FOREST — statsmodels OLS coefficients with 95% CI."""

from __future__ import annotations

import numpy as np
import statsmodels.api as sm
from labcore.eval.regression.plots import plot_coef_forest


def test_coef_forest_matches_statsmodels_conf_int():
    rng = np.random.default_rng(42)
    n = 80
    x1 = rng.normal(size=n)
    x2 = rng.uniform(-1.0, 1.0, n)
    y = 0.4 + 1.5 * x1 - 0.7 * x2 + rng.normal(0.0, 0.25, n)
    exog = sm.add_constant(np.column_stack([x1, x2]), has_constant="add")
    names = ["const", "x1", "x2"]
    model = sm.OLS(y, exog).fit()
    conf = np.asarray(model.conf_int(alpha=0.05))
    params = np.asarray(model.params)

    art = plot_coef_forest(names, params, conf, alpha=0.05)
    assert art["id"] == "REE.P.COEF_FOREST"
    assert art["plotly"]["data"]
    nums = art["numbers"]
    np.testing.assert_allclose(nums["params"], params, atol=1e-12)
    np.testing.assert_allclose(nums["ci_lower"], conf[:, 0], atol=1e-12)
    np.testing.assert_allclose(nums["ci_upper"], conf[:, 1], atol=1e-12)
    assert nums["names"] == names