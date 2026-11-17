"""REE.P.COOKS — stem-style Cook's distance with 4/n threshold."""

from __future__ import annotations

import numpy as np
from labcore.eval.regression.plots import plot_cooks_distance


def test_cooks_stem_and_four_over_n_threshold():
    rng = np.random.default_rng(42)
    cooks = rng.uniform(0.0, 0.12, 80)
    cooks[17] = 0.55
    art = plot_cooks_distance(cooks)
    assert art["id"] == "REE.P.COOKS"
    assert art["plotly"]["data"]
    nums = art["numbers"]
    n = len(cooks)
    assert nums["n"] == n
    assert nums["threshold_4_over_n"] == 4.0 / n
    np.testing.assert_allclose(nums["cooks_d"], cooks, atol=1e-12)
    np.testing.assert_allclose(nums["index"], np.arange(n), atol=1e-12)