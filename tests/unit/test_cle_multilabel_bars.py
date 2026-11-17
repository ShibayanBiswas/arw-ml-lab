"""CLE.P.MULTILABEL_BARS."""

from __future__ import annotations

import numpy as np
from sklearn.metrics import f1_score

from labcore.eval.classification.plots import plot_multilabel_bars


def test_multilabel_bars():
    y_true = np.array([[1, 0, 1], [0, 1, 0], [1, 1, 0], [0, 0, 1]])
    y_pred = np.array([[1, 0, 0], [0, 1, 0], [1, 0, 0], [0, 0, 1]])
    art = plot_multilabel_bars(y_true, y_pred, label_names=["a", "b", "c"])
    assert art["id"] == "CLE.P.MULTILABEL_BARS"
    expected = f1_score(y_true, y_pred, average=None, zero_division=np.nan)
    for name, f1 in art["numbers"]["per_label_f1"].items():
        idx = {"a": 0, "b": 1, "c": 2}[name]
        assert f1 == expected[idx]
    assert art["numbers"]["cardinality_hist"]["2"] == 2
    assert "plotly" in art and art["plotly"]["data"]