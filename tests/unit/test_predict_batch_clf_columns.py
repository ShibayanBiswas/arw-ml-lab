"""Batch classification confidence columns — oneshot-c252 (§45.4)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression

from labcore.predict.score import predict_batch


def test_predict_batch_emits_clf_confidence_columns() -> None:
    X, y = make_classification(
        n_samples=40, n_features=4, n_informative=3, n_redundant=0, random_state=42
    )
    est = LogisticRegression(max_iter=200, random_state=42).fit(X, y)
    frame = pd.DataFrame(X[:8], columns=[f"f{i}" for i in range(4)])
    out = predict_batch(est, frame, feature_names=list(frame.columns))
    assert "pred_confidence" in out
    assert "pred_margin" in out
    assert "pred_entropy" in out
    conf = np.asarray(out["pred_confidence"])
    assert conf.shape == (8,)
    assert np.all((conf >= 0.0) & (conf <= 1.0))
    ent = np.asarray(out["pred_entropy"])
    assert np.all((ent >= 0.0) & (ent <= 1.0 + 1e-9))
