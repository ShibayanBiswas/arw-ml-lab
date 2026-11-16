"""CLE.P.CM_CV."""

from __future__ import annotations

import numpy as np
from labcore.eval.classification.plots import plot_cm_cv


def test_cm_cv():
    cms = [
        np.array([[8, 2], [1, 9]], dtype=float),
        np.array([[7, 3], [2, 8]], dtype=float),
        np.array([[9, 1], [0, 10]], dtype=float),
    ]
    art = plot_cm_cv(cms, labels=[0, 1])
    assert art["id"] == "CLE.P.CM_CV"
    assert np.allclose(np.sum(art["numbers"]["pooled_counts"], axis=1), [30, 30])
