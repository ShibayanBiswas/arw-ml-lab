"""REE.P.COVERAGE_BIN — MAPIE coverage by ŷ-decile vs nominal."""

from __future__ import annotations

import numpy as np
from mapie.metrics.regression import regression_coverage_score, regression_mean_width_score
from mapie.regression import SplitConformalRegressor
from mapie.utils import train_conformalize_test_split
from sklearn.base import clone
from sklearn.datasets import make_regression
from sklearn.linear_model import Ridge

from labcore.eval.regression.plots import plot_coverage_bin


def _decile_coverage_oracle(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_lower: np.ndarray,
    y_upper: np.ndarray,
    *,
    n_bins: int = 10,
) -> list[tuple[int, float]]:
    yp = np.asarray(y_pred, dtype=float)
    edges = np.quantile(yp, np.linspace(0, 1, n_bins + 1))
    edges = np.unique(edges)
    labels = np.digitize(yp, edges[1:-1], right=True) if len(edges) >= 3 else np.zeros(len(yp), int)
    out: list[tuple[int, float]] = []
    yt = np.asarray(y_true, dtype=float).ravel()
    lo = np.asarray(y_lower, dtype=float).ravel()
    hi = np.asarray(y_upper, dtype=float).ravel()
    for decile in sorted(np.unique(labels)):
        mask = labels == decile
        if not np.any(mask):
            continue
        intervals = np.stack([lo[mask], hi[mask]], axis=1)[:, :, np.newaxis]
        cov = float(regression_coverage_score(yt[mask], intervals)[0])
        out.append((int(decile), cov))
    return out


def test_coverage_bin_synthetic_gap_and_oracle():
    rng = np.random.default_rng(42)
    n = 100
    y_pred = np.linspace(-2, 2, n)
    y_true = y_pred + rng.normal(0, 0.3, size=n)
    half_w = np.where(y_pred < 0, 0.2, 1.5)
    y_lower = y_pred - half_w
    y_upper = y_pred + half_w
    nominal = 0.9
    art = plot_coverage_bin(
        y_true, y_pred, y_lower, y_upper, confidence_level=nominal, n_bins=10
    )
    assert art["id"] == "REE.P.COVERAGE_BIN"
    intervals = np.stack([y_lower, y_upper], axis=1)[:, :, np.newaxis]
    assert art["numbers"]["picp"] == float(regression_coverage_score(y_true, intervals)[0])
    oracle = _decile_coverage_oracle(y_true, y_pred, y_lower, y_upper, n_bins=10)
    assert len(art["numbers"]["by_decile"]) == len(oracle)
    for row, (dec, cov) in zip(art["numbers"]["by_decile"], oracle, strict=True):
        assert row["decile"] == dec
        assert row["coverage"] == cov
    gap = max(abs(cov - nominal) for _, cov in oracle)
    assert art["numbers"]["conditional_coverage_gap"] == gap
    assert gap > 0.05


def test_coverage_bin_mapie_split_conformal():
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
    art = plot_coverage_bin(
        y_test, y_pred_arr, y_lower, y_upper, confidence_level=level, n_bins=10
    )
    assert art["numbers"]["n"] == len(y_test)
    intervals = np.stack([y_lower, y_upper], axis=1)[:, :, np.newaxis]
    assert art["numbers"]["picp"] == float(regression_coverage_score(y_test, intervals)[0])
    assert art["numbers"]["mean_interval_width"] == float(
        np.asarray(regression_mean_width_score(intervals)).ravel()[0]
    )
    assert art["numbers"]["conditional_coverage_gap"] is not None
    assert "plotly" in art and art["plotly"]["data"]