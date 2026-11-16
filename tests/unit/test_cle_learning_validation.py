"""CLE.P.LEARNING / CLE.P.VALIDATION via sklearn curves."""

from __future__ import annotations

import numpy as np
from labcore.eval.classification.plots import plot_learning_curve, plot_validation_curve
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression


def test_learning_and_validation_curves():
    data = load_breast_cancer()
    X = data.data[:180]
    y = data.target[:180]
    est = LogisticRegression(max_iter=2000, random_state=42)
    learn = plot_learning_curve(est, X, y, cv=3, seed=42)
    assert learn["id"] == "CLE.P.LEARNING"
    assert "plotly" in learn
    assert len(learn["numbers"]["train_sizes"]) == 5
    val = plot_validation_curve(
        LogisticRegression(max_iter=2000, random_state=42),
        X,
        y,
        param_name="C",
        param_range=[0.1, 1.0, 10.0],
        cv=3,
    )
    assert val["id"] == "CLE.P.VALIDATION"
    assert np.isfinite(learn["numbers"]["val_mean"]).all()
