"""CLE.P.CM_MULTILABEL."""

from __future__ import annotations

import numpy as np
from labcore.eval.classification.plots import plot_cm_multilabel


def test_cm_multilabel():
    y_true = np.array([[1, 0, 1], [0, 1, 0], [1, 1, 0], [0, 0, 1]])
    y_pred = np.array([[1, 0, 0], [0, 1, 0], [1, 0, 0], [0, 0, 1]])
    art = plot_cm_multilabel(y_true, y_pred, label_names=["a", "b", "c"])
    assert art["id"] == "CLE.P.CM_MULTILABEL"
    assert len(art["numbers"]["matrices"]) == 3
