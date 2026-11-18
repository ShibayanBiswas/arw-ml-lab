"""Batch conformal prediction sets — oneshot-c259 (§45.4)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from labcore.predict.score import predict_batch, try_predict_sets


class _FakeSetPipe:
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return np.zeros(len(X), dtype=int)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        n = len(X)
        return np.tile([0.2, 0.8], (n, 1))

    def predict_set(self, X: pd.DataFrame):  # noqa: ANN201
        n = len(X)
        y_pred = np.ones(n, dtype=int)
        # boolean membership matrix (n, 2)
        y_ps = np.zeros((n, 2), dtype=bool)
        y_ps[:, 1] = True
        y_ps[0, 0] = True  # first row includes both classes
        return y_pred, y_ps


def test_try_predict_sets() -> None:
    frame = pd.DataFrame({"a": [1.0, 2.0]})
    out = try_predict_sets(_FakeSetPipe(), frame)
    assert out is not None
    assert out["pred_set"][0] == [0, 1]
    assert out["pred_set"][1] == [1]


def test_predict_batch_includes_pred_set() -> None:
    frame = pd.DataFrame({"a": [1.0, 2.0, 3.0]})
    out = predict_batch(_FakeSetPipe(), frame, feature_names=["a"])
    assert "pred_set" in out
    assert "pred_set" in out["classification_columns"]
