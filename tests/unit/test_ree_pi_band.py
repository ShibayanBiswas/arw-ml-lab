"""REE.P.PI_BAND — MAPIE prediction interval band sorted by ŷ."""

from __future__ import annotations

import numpy as np
from mapie.metrics.regression import regression_coverage_score, regression_mean_width_score
from mapie.regression import SplitConformalRegressor
from mapie.utils import train_conformalize_test_split
from sklearn.base import clone
from sklearn.datasets import make_regression
from sklearn.linear_model import Ridge

from labcore.eval.regression.plots import plot_pi_band


def test_pi_band_synthetic_matches_mapie_metrics():
    y_true = np.array([1.0, 2.0, 3.0, 4.0])
    y_pred = np.array([1.1, 1.9, 3.2, 3.8])
    y_lower = y_pred - 0.5
    y_upper = y_pred + 0.5
    art = plot_pi_band(y_true, y_pred, y_lower, y_upper, confidence_level=0.9)
    assert art["id"] == "REE.P.PI_BAND"
    intervals = np.stack([y_lower, y_upper], axis=1)[:, :, np.newaxis]
    expected_cov = float(regression_coverage_score(y_true, intervals)[0])
    assert art["numbers"]["picp"] == expected_cov
    assert art["numbers"]["mean_interval_width"] == float(
        np.asarray(regression_mean_width_score(intervals)).ravel()[0]
    )
    order = np.argsort(y_pred, kind="stable")
    assert art["numbers"]["y_pred_sorted"] == y_pred[order].tolist()


def test_pi_band_mapie_split_conformal():
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
    y_test = np.asarray(y_test).ravel()
    art = plot_pi_band(y_test, y_pred_arr, y_lower, y_upper, confidence_level=level)
    assert art["numbers"]["n"] == len(y_test)
    intervals = np.stack([y_lower, y_upper], axis=1)[:, :, np.newaxis]
    assert art["numbers"]["picp"] == float(regression_coverage_score(y_test, intervals)[0])
    assert "plotly" in art and art["plotly"]["data"]