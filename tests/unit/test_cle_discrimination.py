"""CLE.P.DISCRIMINATION."""

from __future__ import annotations

import numpy as np
from labcore.eval.classification.plots import plot_discrimination


def test_discrimination_plot():
    rng = np.random.default_rng(42)
    y = np.r_[np.zeros(50, dtype=int), np.ones(50, dtype=int)]
    scores = np.clip(y.astype(float) + rng.normal(0, 0.25, size=y.shape), 0, 1)
    art = plot_discrimination(y, scores, n_splits=10, seed=42)
    assert art["id"] == "CLE.P.DISCRIMINATION"
    assert len(art["numbers"]["f1_mean"]) == 19
