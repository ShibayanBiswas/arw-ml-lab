"""REE.P.VALIDATION — regression validation curve via sklearn."""

from __future__ import annotations

import numpy as np
from labcore.eval.regression.plots import plot_regression_validation_curve
from sklearn.datasets import make_regression
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold, ValidationCurveDisplay, validation_curve


def test_regression_validation_curve_matches_sklearn():
    X, y = make_regression(n_samples=120, n_features=6, noise=8.0, random_state=42)
    param_range = [0.01, 0.1, 1.0, 10.0]
    est = Ridge(random_state=42)
    art = plot_regression_validation_curve(
        est,
        X,
        y,
        param_name="alpha",
        param_range=param_range,
        cv=3,
        seed=42,
    )
    assert art["id"] == "REE.P.VALIDATION"
    assert art["numbers"]["scoring"] == "neg_mean_squared_error"
    assert art["plotly"]["data"]

    cv_splitter = KFold(n_splits=3, shuffle=True, random_state=42)
    train_scores, val_scores = validation_curve(
        Ridge(random_state=42),
        X,
        y,
        param_name="alpha",
        param_range=param_range,
        cv=cv_splitter,
        scoring="neg_mean_squared_error",
        n_jobs=1,
    )
    np.testing.assert_allclose(art["numbers"]["train_mean"], np.mean(train_scores, axis=1), rtol=1e-9)
    np.testing.assert_allclose(art["numbers"]["val_mean"], np.mean(val_scores, axis=1), rtol=1e-9)

    display = ValidationCurveDisplay.from_estimator(
        Ridge(random_state=42),
        X,
        y,
        param_name="alpha",
        param_range=param_range,
        cv=cv_splitter,
        scoring="neg_mean_squared_error",
        n_jobs=1,
    )
    np.testing.assert_allclose(art["numbers"]["train_mean"], display.train_scores.mean(axis=1), rtol=1e-9)
    np.testing.assert_allclose(art["numbers"]["val_mean"], display.test_scores.mean(axis=1), rtol=1e-9)