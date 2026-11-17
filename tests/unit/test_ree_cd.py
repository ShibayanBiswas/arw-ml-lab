"""REE.P.CD — regression critical-difference diagram."""

from __future__ import annotations

import numpy as np
from labcore.eval.regression.plots import plot_regression_cd


def test_regression_cd_rmse_lower_is_better():
    rng = np.random.default_rng(42)
    n_folds = 8
    fold_scores = {
        "ridge": rng.uniform(0.85, 0.95, n_folds),
        "rf": rng.uniform(1.05, 1.25, n_folds),
        "gbrt": rng.uniform(1.0, 1.2, n_folds),
    }
    art = plot_regression_cd(fold_scores, metric="rmse")
    assert art["id"] == "REE.P.CD"
    assert art["numbers"]["status"] == "ok"
    ranks = art["numbers"]["mean_ranks"]
    assert ranks["ridge"] < ranks["rf"]
    assert art["plotly"]["data"]