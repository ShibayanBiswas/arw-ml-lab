"""REE.P.PIT — quantile calibration PIT histogram."""

from __future__ import annotations

import numpy as np
from scipy import stats
from scipy.interpolate import interp1d

from labcore.eval.regression.plots import _pit_from_quantile_grid, plot_pit


def test_pit_median_and_interp_oracle():
    n = 80
    mu = np.linspace(-2.0, 2.0, n)
    levels = np.linspace(0.1, 0.9, 9)
    sigma = 0.8
    y_quantiles = mu[:, None] + sigma * stats.norm.ppf(levels)[None, :]
    y_true = mu.copy()
    pit = _pit_from_quantile_grid(y_true, y_quantiles, levels)
    np.testing.assert_allclose(pit, 0.5, rtol=1e-9, atol=1e-9)

    rng = np.random.default_rng(42)
    y_obs = rng.normal(loc=mu, scale=sigma)
    oracle = np.empty(n, dtype=float)
    for i in range(n):
        q_sorted = y_quantiles[i, :]
        tau_sorted = levels
        cdf = interp1d(
            q_sorted,
            tau_sorted,
            bounds_error=False,
            fill_value="extrapolate",
            assume_sorted=True,
        )
        oracle[i] = float(np.clip(cdf(float(y_obs[i])), 0.0, 1.0))
    pit_obs = _pit_from_quantile_grid(y_obs, y_quantiles, levels)
    np.testing.assert_allclose(pit_obs, oracle, rtol=1e-12, atol=1e-12)


def test_pit_histogram_and_kstest_numbers():
    rng = np.random.default_rng(42)
    n = 80
    levels = np.linspace(0.1, 0.9, 5)
    y_true = rng.uniform(0.0, 1.0, size=n)
    y_quantiles = y_true[:, None] + np.linspace(-1.0, 1.0, len(levels))[None, :]
    art = plot_pit(y_true, y_quantiles, quantile_levels=levels, n_bins=10)
    assert art["id"] == "REE.P.PIT"
    pit = np.asarray(art["numbers"]["pit"], dtype=float)
    ks = stats.kstest(pit, stats.uniform(loc=0.0, scale=1.0).cdf)
    assert art["numbers"]["ks_statistic"] == float(ks.statistic)
    assert art["numbers"]["ks_pvalue"] == float(ks.pvalue)
    counts, edges = np.histogram(pit, bins=10, range=(0.0, 1.0), density=True)
    np.testing.assert_allclose(art["numbers"]["hist_density"], counts, rtol=1e-12, atol=1e-12)
    assert art["numbers"]["n"] == n
    assert art["plotly"]["data"]