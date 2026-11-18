"""Deep ensemble thin wrapper — oneshot-c261."""

from __future__ import annotations

import numpy as np

from labcore.uncertainty.deep_ensemble import ARTEFACT_ID, deep_ensemble_predict


def test_deep_ensemble_mean_std() -> None:
    x = np.array([[1.0], [2.0]])

    def m1(z: np.ndarray) -> np.ndarray:
        return z * 2.0

    def m2(z: np.ndarray) -> np.ndarray:
        return z * 2.0 + 1.0

    out = deep_ensemble_predict([m1, m2], x, seed=42)
    assert out["id"] == ARTEFACT_ID
    assert out["n_members"] == 2
    assert out["refit"] is False
    mean = np.asarray(out["mean"])
    assert mean.shape == (2, 1)
    # member preds differ → positive std
    assert float(np.asarray(out["std"]).mean()) > 0
