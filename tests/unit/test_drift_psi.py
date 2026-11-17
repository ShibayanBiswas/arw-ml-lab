"""PSI drift monitor tests."""

from __future__ import annotations

import numpy as np
from labcore.monitoring import psi_drift_report


def test_psi_detects_shift() -> None:
    rng = np.random.default_rng(42)
    ref = rng.normal(0, 1, size=(200, 2))
    cur = rng.normal(2.5, 1.2, size=(200, 2))
    out = psi_drift_report(ref, cur, feature_names=["a", "b"], drift_threshold=0.2)
    assert out["id"] == "MON.T.PSI_DRIFT"
    assert out["seed"] == 42
    assert out["n_drifted"] >= 1
    assert all(r["status"] == "ok" for r in out["features"])


def test_psi_same_distribution_low() -> None:
    rng = np.random.default_rng(42)
    ref = rng.normal(0, 1, size=(300, 1))
    cur = rng.normal(0, 1, size=(300, 1))
    out = psi_drift_report(ref, cur, drift_threshold=0.5)
    assert out["features"][0]["status"] == "ok"
    assert np.isfinite(out["features"][0]["psi"])