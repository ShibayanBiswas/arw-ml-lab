"""REE.P.ERR_SEGMENT + REE.P.ERR_HEATMAP."""

from __future__ import annotations

import numpy as np
from labcore.eval.regression.plots import plot_err_heatmap, plot_err_segment


def test_err_segment_and_heatmap():
    rng = np.random.default_rng(42)
    y = rng.normal(10, 2, 200)
    pred = y + rng.normal(0, 0.8, 200)
    seg = plot_err_segment(y, pred, n_bins=5)
    assert seg["id"] == "REE.P.ERR_SEGMENT"
    assert np.isfinite(seg["numbers"]["overall_mae"])
    x = rng.normal(0, 1, 200)
    z = rng.normal(0, 1, 200)
    heat = plot_err_heatmap(y, pred, x, z, bins=4)
    assert heat["id"] == "REE.P.ERR_HEATMAP"
