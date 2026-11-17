"""REE.P.LEARNING — regression learning curve via sklearn."""

from __future__ import annotations

import numpy as np
from labcore.eval.regression.plots import plot_regression_learning_curve
from sklearn.datasets import load_diabetes
from sklearn.linear_model import Ridge
from sklearn.model_selection import learning_curve


def test_regression_learning_curve_matches_sklearn():
    data = load_diabetes()
    X = data.data[:200]
    y = data.target[:200]
    est = Ridge(random_state=42)
    art = plot_regression_learning_curve(est, X, y, cv=3, seed=42)
    assert art["id"] == "REE.P.LEARNING"
    assert art["plotly"]["data"]
    assert len(art["numbers"]["train_sizes"]) == 5

    train_sizes, train_scores, val_scores = learning_curve(
        est,
        X,
        y,
        cv=3,
        scoring="r2",
        random_state=42,
        shuffle=True,
        n_jobs=1,
        train_sizes=np.linspace(0.3, 1.0, 5),
    )
    np.testing.assert_allclose(art["numbers"]["train_sizes"], train_sizes)
    np.testing.assert_allclose(
        art["numbers"]["train_mean"],
        np.mean(train_scores, axis=1),
        rtol=0,
        atol=1e-9,
    )
    np.testing.assert_allclose(
        art["numbers"]["val_mean"],
        np.mean(val_scores, axis=1),
        rtol=0,
        atol=1e-9,
    )
    assert np.isfinite(art["numbers"]["val_mean"]).all()