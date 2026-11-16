"""KS drift monitor tests."""

from __future__ import annotations

import numpy as np
from labcore.monitoring import ks_drift_report


def test_ks_detects_shift():
    rng = np.random.default_rng(42)
    ref = rng.normal(0, 1, size=(200, 2))
    cur = rng.normal(3, 1, size=(200, 2))  # clear shift
    out = ks_drift_report(ref, cur, feature_names=["a", "b"], alpha=0.01)
    assert out["n_drifted"] >= 1
    assert all(r["status"] == "ok" for r in out["features"])


def test_ks_same_distribution_low_drift():
    rng = np.random.default_rng(42)
    ref = rng.normal(0, 1, size=(300, 1))
    cur = rng.normal(0, 1, size=(300, 1))
    out = ks_drift_report(ref, cur, alpha=0.001)
    # may or may not flag — just ensure computable
    assert out["features"][0]["status"] == "ok"
    assert np.isfinite(out["features"][0]["pvalue"])
