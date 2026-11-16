"""CLE.P.CM_FOLDS."""

from __future__ import annotations

import numpy as np
from labcore.eval.classification.plots import plot_cm_folds


def test_cm_folds():
    cms = [
        np.array([[8, 2], [1, 9]], dtype=float),
        np.array([[7, 3], [2, 8]], dtype=float),
        np.array([[9, 1], [0, 10]], dtype=float),
    ]
    art = plot_cm_folds(cms, labels=[0, 1])
    assert art["id"] == "CLE.P.CM_FOLDS"
    assert len(art["numbers"]["fold_cms_row_norm"]) == 3
