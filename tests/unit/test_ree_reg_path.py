"""REE.P.REG_PATH — sklearn lasso_path / enet_path coefficient paths."""

from __future__ import annotations

import numpy as np
from labcore.eval.regression.plots import plot_reg_path
from sklearn.datasets import make_regression
from sklearn.linear_model import enet_path, lasso_path


def test_reg_path_lasso_matches_sklearn():
    X, y = make_regression(n_samples=100, n_features=5, noise=6.0, random_state=42)
    n_alphas = 12
    art = plot_reg_path(X, y, kind="lasso", alphas=n_alphas, seed=42)
    assert art["id"] == "REE.P.REG_PATH"
    assert art["numbers"]["path_kind"] == "lasso"
    assert len(art["plotly"]["data"]) == 5

    alphas_oracle, coefs_oracle, _ = lasso_path(X, y, alphas=n_alphas)
    np.testing.assert_allclose(art["numbers"]["alphas"], alphas_oracle, rtol=1e-12)
    np.testing.assert_allclose(art["numbers"]["coefs"], coefs_oracle, rtol=1e-9)


def test_reg_path_enet_and_ridge_match_sklearn():
    X, y = make_regression(n_samples=80, n_features=4, noise=5.0, random_state=42)
    l1_ratio = 0.35
    art_enet = plot_reg_path(X, y, kind="enet", l1_ratio=l1_ratio, alphas=10, seed=42)
    a_e, c_e, _ = enet_path(X, y, alphas=10, l1_ratio=l1_ratio)
    np.testing.assert_allclose(art_enet["numbers"]["coefs"], c_e, rtol=1e-9)

    ridge_alphas = np.logspace(-1, 2, 8)
    art_ridge = plot_reg_path(X, y, kind="ridge", alphas=ridge_alphas, seed=42)
    a_r, c_r, _ = enet_path(X, y, alphas=ridge_alphas, l1_ratio=0.0)
    np.testing.assert_allclose(art_ridge["numbers"]["coefs"], c_r, rtol=1e-9)
    np.testing.assert_allclose(art_ridge["numbers"]["l1_ratio"], 0.0)