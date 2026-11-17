"""REE.P.LEVERAGE — studentised residual vs leverage with Cook's D contours."""

from __future__ import annotations

import numpy as np
import statsmodels.api as sm
from labcore.eval.regression.plots import _cooks_contour_studentised, plot_leverage_studentised


def test_leverage_plot_matches_ols_influence_and_contours():
    rng = np.random.default_rng(42)
    n = 60
    y_pred = rng.uniform(0.0, 5.0, n)
    y_true = 1.2 * y_pred + rng.normal(0.0, 0.35, n)

    exog = sm.add_constant(y_pred)
    model = sm.OLS(y_true, exog).fit()
    infl = model.get_influence()
    leverage = np.asarray(infl.hat_matrix_diag)
    student = np.asarray(infl.resid_studentized_internal)
    p = exog.shape[1]

    art = plot_leverage_studentised(leverage, student, n_params=p)
    assert art["id"] == "REE.P.LEVERAGE"
    assert art["plotly"]["data"]
    nums = art["numbers"]
    np.testing.assert_allclose(nums["leverage"], leverage, atol=1e-12)
    np.testing.assert_allclose(nums["studentised_resid"], student, atol=1e-12)
    assert nums["cooks_levels"] == [0.5, 1.0]

    cooks = np.asarray(infl.cooks_distance[0])
    implied = student**2 / p * leverage / (1.0 - leverage)
    np.testing.assert_allclose(implied, cooks, atol=1e-10)

    for level in (0.5, 1.0):
        h_line = np.asarray(nums["contours"][f"cooks_{level:g}_h"])
        y_line = np.asarray(nums["contours"][f"cooks_{level:g}_abs_stud"])
        oracle = _cooks_contour_studentised(h_line, level, p)
        np.testing.assert_allclose(y_line, oracle, atol=1e-12)
        on_curve = y_line**2 / p * h_line / (1.0 - h_line)
        np.testing.assert_allclose(on_curve, level, rtol=1e-9)