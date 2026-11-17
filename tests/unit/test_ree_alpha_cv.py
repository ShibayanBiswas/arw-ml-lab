"""REE.P.ALPHA_CV — LassoCV / RidgeCV mse_path vs alphas_."""

from __future__ import annotations

import numpy as np
from labcore.eval.regression.plots import plot_alpha_cv
from sklearn.datasets import make_regression
from sklearn.linear_model import LassoCV, RidgeCV
from sklearn.model_selection import KFold


def test_alpha_cv_lasso_matches_sklearn():
    X, y = make_regression(n_samples=100, n_features=8, noise=6.0, random_state=42)
    alphas = np.logspace(-2, 1, 15)
    cv = 4
    art = plot_alpha_cv(X, y, kind="lasso", cv=cv, seed=42, alphas=alphas)
    assert art["id"] == "REE.P.ALPHA_CV"
    assert art["numbers"]["path_kind"] == "lasso"

    cv_splitter = KFold(n_splits=cv, shuffle=True, random_state=42)
    oracle = LassoCV(alphas=alphas, cv=cv_splitter, random_state=42)
    oracle.fit(X, y)
    np.testing.assert_allclose(art["numbers"]["alphas"], oracle.alphas_, rtol=1e-12)
    np.testing.assert_allclose(art["numbers"]["mse_path"], oracle.mse_path_, rtol=1e-9)
    np.testing.assert_allclose(art["numbers"]["alpha_best"], oracle.alpha_, rtol=1e-12)


def test_alpha_cv_ridge_matches_sklearn():
    X, y = make_regression(n_samples=90, n_features=5, noise=5.0, random_state=42)
    alphas = [0.05, 0.5, 5.0, 50.0]
    cv = 3
    art = plot_alpha_cv(X, y, kind="ridge", cv=cv, seed=42, alphas=alphas)
    assert art["numbers"]["path_kind"] == "ridge"

    from sklearn.linear_model import Ridge
    from sklearn.model_selection import validation_curve

    cv_splitter = KFold(n_splits=cv, shuffle=True, random_state=42)
    oracle = RidgeCV(alphas=alphas, cv=cv_splitter)
    oracle.fit(X, y)
    _, neg_val = validation_curve(
        Ridge(),
        X,
        y,
        param_name="alpha",
        param_range=alphas,
        cv=cv_splitter,
        scoring="neg_mean_squared_error",
        n_jobs=1,
    )
    np.testing.assert_allclose(art["numbers"]["mse_path"], -neg_val, rtol=1e-9)
    np.testing.assert_allclose(art["numbers"]["alpha_best"], oracle.alpha_, rtol=1e-12)