"""CLE.P.PER_CLASS_BARS."""

from __future__ import annotations

import numpy as np
from labcore.eval.classification.plots import plot_per_class_bars
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def test_per_class_bars_cv_error_bars():
    data = load_iris()
    X, y = data.data, data.target
    pipe = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=500, random_state=42)),
        ]
    )
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    fold_true: list[np.ndarray] = []
    fold_pred: list[np.ndarray] = []
    for train, test in cv.split(X, y):
        pipe.fit(X[train], y[train])
        fold_true.append(y[test])
        fold_pred.append(pipe.predict(X[test]))

    art = plot_per_class_bars(fold_true, fold_pred, labels=[0, 1, 2])
    assert art["id"] == "CLE.P.PER_CLASS_BARS"
    assert art["numbers"]["n_folds"] == 5
    assert set(art["numbers"]["f1_mean"]) == {"0", "1", "2"}
    assert "f1_std" in art["numbers"]
    assert all(v >= 0 for v in art["numbers"]["f1_std"].values())