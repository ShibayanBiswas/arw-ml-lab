"""OOF residual conformal attach — oneshot-c249."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from labcore.predict.conformal_attach import (
    attach_oof_residual_qhat,
    oof_absolute_residual_qhat,
)
from labcore.predict.score import predict_batch


def test_oof_qhat_and_batch_intervals() -> None:
    rng = np.random.default_rng(42)
    y_true = rng.normal(size=50)
    y_pred = y_true + rng.normal(scale=0.5, size=50)
    q = oof_absolute_residual_qhat(y_true, y_pred, confidence_level=0.9)
    assert q > 0

    X = rng.normal(size=(50, 2))
    pipe = Pipeline([("sc", StandardScaler()), ("lr", LinearRegression())])
    pipe.fit(X, y_true)
    pipe = attach_oof_residual_qhat(pipe, y_true, y_pred, confidence_level=0.9)
    assert getattr(pipe, "conformal_qhat_") == q

    frame = pd.DataFrame(X[:5], columns=["a", "b"])
    out = predict_batch(pipe, frame, feature_names=["a", "b"], confidence_level=0.9)
    assert out["pred_interval_method"] == "split_conformal_residual"
    assert "pred_lower_90" in out
    widths = np.asarray(out["pred_upper_90"]) - np.asarray(out["pred_lower_90"])
    assert np.allclose(widths, 2 * q)
