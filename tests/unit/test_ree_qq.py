"""REE.P.QQ — residual normal Q-Q with statsmodels ProbPlot + 95% envelope."""

from __future__ import annotations

import numpy as np
from labcore.eval.regression.plots import plot_qq
from scipy import stats
from statsmodels.graphics.gofplots import ProbPlot


def test_qq_probplot_and_envelope_match_libraries():
    rng = np.random.default_rng(42)
    resid = rng.normal(0.2, 1.1, 88)
    alpha = 0.05
    art = plot_qq(resid, alpha=alpha)
    assert art["id"] == "REE.P.QQ"
    assert art["plotly"]["data"]
    nums = art["numbers"]

    pp = ProbPlot(resid, dist=stats.norm, fit=False)
    np.testing.assert_allclose(nums["theoretical_quantiles"], pp.theoretical_quantiles, atol=1e-12)
    np.testing.assert_allclose(nums["sample_quantiles"], pp.sample_quantiles, atol=1e-12)

    n = len(resid)
    mu = float(np.mean(resid))
    sd = float(np.std(resid, ddof=1))
    ranks = np.arange(1, n + 1, dtype=float)
    lo_p = stats.beta.ppf(alpha / 2, ranks, n - ranks + 1)
    hi_p = stats.beta.ppf(1.0 - alpha / 2, ranks, n - ranks + 1)
    env_lo = mu + sd * stats.norm.ppf(lo_p)
    env_hi = mu + sd * stats.norm.ppf(hi_p)
    ref_y = np.asarray(pp.theoretical_quantiles) * sd + mu

    np.testing.assert_allclose(nums["envelope_lo"], env_lo, atol=1e-10)
    np.testing.assert_allclose(nums["envelope_hi"], env_hi, atol=1e-10)
    np.testing.assert_allclose(nums["reference_y"], ref_y, atol=1e-12)
    assert nums["mu"] == mu
    assert nums["sd"] == sd