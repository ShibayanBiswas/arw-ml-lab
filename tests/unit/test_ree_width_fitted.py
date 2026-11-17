"""REE.P.WIDTH_FITTED — MAPIE interval width vs ŷ."""

from __future__ import annotations

import numpy as np
from mapie.metrics.regression import regression_mean_width_score
from mapie.regression import SplitConformalRegressor
from mapie.utils import train_conformalize_test_split
from sklearn.base import clone
from sklearn.datasets import make_regression
from sklearn.linear_model import Ridge
from statsmodels.nonparametric.smoothers_lowess import lowess

from labcore.eval.regression.plots import plot_width_fitted


def test_width_fitted_oracle_lowess_and_mpiw():
    rng = np.random.default_rng(42)
    n = 80
    y_pred = np.linspace(-3, 3, n)
    half_w = 0.5 + 0.4 * np.abs(y_pred)
    y_lower = y_pred - half_w
    y_upper = y_pred + half_w
    art = plot_width_fitted(y_pred, y_lower, y_upper, confidence_level=0.9)
    assert art["id"] == "REE.P.WIDTH_FITTED"
    intervals = np.stack([y_lower, y_upper], axis=1)[:, :, np.newaxis]
    oracle_mpiw = float(np.asarray(regression_mean_width_score(intervals)).ravel()[0])
    assert art["numbers"]["mean_interval_width"] == oracle_mpiw
    width = y_upper - y_lower
    smooth = lowess(width, y_pred, frac=0.3, return_sorted=True)
    np.testing.assert_allclose(art["numbers"]["lowess_y"], smooth[:, 1], rtol=1e-9, atol=1e-9)
    assert art["numbers"]["n"] == n
    assert art["plotly"]["data"]


def test_width_fitted_mapie_split_conformal():
    X, y = make_regression(n_samples=200, n_features=6, noise=8.0, random_state=42)
    X_train, X_conf, X_test, y_train, y_conf, y_test = train_conformalize_test_split(
        X,
        y,
        train_size=0.5,
        conformalize_size=0.25,
        test_size=0.25,
        random_state=42,
    )
    level = 0.9
    mapie = SplitConformalRegressor(
        estimator=clone(Ridge()),
        confidence_level=level,
        conformity_score="absolute",
        prefit=False,
    )
    mapie.fit(X_train, y_train)
    mapie.conformalize(X_conf, y_conf)
    y_pred, y_pis = mapie.predict_interval(X_test)
    pis = np.asarray(y_pis)
    y_lower = pis[:, 0, 0]
    y_upper = pis[:, 1, 0]
    y_pred_arr = np.asarray(y_pred).ravel()
    art = plot_width_fitted(y_pred_arr, y_lower, y_upper, confidence_level=level)
    intervals = np.stack([y_lower, y_upper], axis=1)[:, :, np.newaxis]
    assert art["numbers"]["mean_interval_width"] == float(
        np.asarray(regression_mean_width_score(intervals)).ravel()[0]
    )
    assert len(art["numbers"]["width"]) == len(y_pred_arr)