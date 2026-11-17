"""REE.P.RESID_HIST — histogram + scipy KDE + normal overlay."""

from __future__ import annotations

import numpy as np
from labcore.eval.regression.plots import plot_residual_hist
from scipy import stats
from scipy.stats import gaussian_kde


def test_resid_hist_matches_scipy_kde_and_normal_pdf():
    rng = np.random.default_rng(42)
    resid = rng.normal(-0.15, 0.95, 120)
    bins = 24
    art = plot_residual_hist(resid, bins=bins)
    assert art["id"] == "REE.P.RESID_HIST"
    assert art["plotly"]["data"]
    nums = art["numbers"]

    finite = resid[np.isfinite(resid)]
    mu = float(np.mean(finite))
    sd = float(np.std(finite, ddof=1))
    density, bin_edges = np.histogram(finite, bins=bins, density=True)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2.0
    lo = float(bin_edges[0])
    hi = float(bin_edges[-1])
    pad = 0.05 * (hi - lo)
    xs = np.linspace(lo - pad, hi + pad, 200)

    np.testing.assert_allclose(nums["bin_centers"], bin_centers, atol=1e-12)
    np.testing.assert_allclose(nums["hist_density"], density, atol=1e-12)
    np.testing.assert_allclose(nums["kde_y"], gaussian_kde(finite)(xs), atol=1e-10)
    np.testing.assert_allclose(nums["normal_y"], stats.norm.pdf(xs, loc=mu, scale=sd), atol=1e-12)
    assert nums["mu"] == mu
    assert nums["sd"] == sd