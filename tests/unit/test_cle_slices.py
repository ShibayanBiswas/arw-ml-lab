"""CLE.P.SLICES via fairlearn MetricFrame."""

from __future__ import annotations

import numpy as np
from labcore.eval.classification.slices import metric_by_segment
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def test_metric_by_segment_binary():
    data = load_breast_cancer()
    X, y = data.data, data.target
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    pipe = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=2000, random_state=42)),
        ]
    )
    pipe.fit(X_tr, y_tr)
    pred = pipe.predict(X_te)
    # Segment by median of first feature
    seg = (X_te[:, 0] >= np.median(X_te[:, 0])).astype(int)
    out = metric_by_segment(y_te, pred, seg, seed=42)
    assert out["id"] == "CLE.T.SLICES"
    plot = out["plots"][0]
    assert plot["id"] == "CLE.P.SLICES"
    assert len(out["rows"]) >= 2
    assert plot["numbers"]["averaging"] == "binary"
    assert plot["numbers"]["overall"]["accuracy"] == out["overall"]["accuracy"]
