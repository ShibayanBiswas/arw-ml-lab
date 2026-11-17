"""Batch predict conformal interval columns — oneshot-c247 (§45.4)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from labcore.predict.score import predict_batch, try_predict_intervals


class _ResidualConformalPipe:
    """Minimal fitted regressor + stored split-conformal residual quantile."""

    def __init__(self, qhat: float = 1.5) -> None:
        self._est = LinearRegression()
        self.conformal_qhat_ = float(qhat)

    def fit(self, X: np.ndarray, y: np.ndarray) -> "_ResidualConformalPipe":
        self._est.fit(X, y)
        return self

    def predict(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        arr = np.asarray(X, dtype=float)
        return self._est.predict(arr)


def test_try_predict_intervals_from_qhat() -> None:
    rng = np.random.default_rng(42)
    X = rng.normal(size=(20, 2))
    y = X[:, 0] * 2.0 + 0.1
    pipe = _ResidualConformalPipe(qhat=1.5).fit(X, y)
    frame = pd.DataFrame(X, columns=["a", "b"])
    iv = try_predict_intervals(pipe, frame, confidence_level=0.9)
    assert iv is not None
    assert iv["pred_interval_method"] == "split_conformal_residual"
    assert len(iv["pred_lower"]) == 20
    widths = np.asarray(iv["pred_upper"]) - np.asarray(iv["pred_lower"])
    assert np.allclose(widths, 3.0)


def test_predict_batch_emits_interval_columns() -> None:
    rng = np.random.default_rng(42)
    X = rng.normal(size=(8, 1))
    y = X[:, 0] + 1.0
    pipe = _ResidualConformalPipe(qhat=0.5).fit(X, y)
    frame = pd.DataFrame(X, columns=["x1"])
    out = predict_batch(pipe, frame, feature_names=["x1"], confidence_level=0.9)
    assert "pred_lower_90" in out
    assert "pred_upper_90" in out
    assert out["pred_interval_method"] == "split_conformal_residual"
    assert out["interval_columns"] == [
        "pred_lower_90",
        "pred_upper_90",
        "pred_interval_method",
    ]


def test_predict_batch_no_intervals_without_wrapper() -> None:
    rng = np.random.default_rng(42)
    X = rng.normal(size=(5, 1))
    y = X[:, 0]
    est = LinearRegression().fit(X, y)
    frame = pd.DataFrame(X, columns=["x1"])
    out = predict_batch(est, frame, feature_names=["x1"])
    assert "interval_columns" not in out
    assert out["n_rows"] == 5
