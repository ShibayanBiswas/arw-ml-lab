"""MI.SEED.DRIFT — ST-ML-02 MI-06 offline (oneshot-c169)."""

from __future__ import annotations

import pytest

from labcore.integrity.seed_drift_contract import (
    ARTEFACT_ID,
    SeedDriftContractError,
    assert_mi06_quick_run_reproduces,
    assert_mi06_seed_change_drifts,
    seed_drift_manifest,
)
from labcore.integrity.seed_drift_policy import (
    LAB_DEFAULT_SEED,
    METRIC_REPRODUCE_ATOL,
    MI06_RULE,
    metrics_close,
    metrics_differ,
)


def test_metrics_close_helpers():
    assert metrics_close(1.0, 1.0 + METRIC_REPRODUCE_ATOL / 10)
    assert metrics_differ(1.0, 1.0 + METRIC_REPRODUCE_ATOL * 10)


def test_mi06_quick_run_reproduces():
    out = assert_mi06_quick_run_reproduces(seed=42)
    assert out["mi_rule"] == MI06_RULE
    assert out["reproduced"] is True
    assert out["lab_default_seed"] == LAB_DEFAULT_SEED


def test_mi06_seed_change_drifts():
    out = assert_mi06_seed_change_drifts(seed=42)
    assert out["drift_detected"] is True
    assert out["cv_mean_seed_42"] != out["cv_mean_seed_43"]


def test_seed_drift_manifest():
    m = seed_drift_manifest(seed=42)
    assert m["id"] == ARTEFACT_ID
    assert m["stress_test"] == "ST-ML-02"
    assert len(m["checks"]) == 2


def test_contract_raises_when_runs_differ(monkeypatch: pytest.MonkeyPatch):
    from labcore.integrity import seed_drift_contract as mod

    calls = {"n": 0}

    def fake_mean(*, seed: int) -> float:
        calls["n"] += 1
        return 0.9 if calls["n"] == 1 else 0.8

    monkeypatch.setattr(mod, "_cv_leaderboard_mean", fake_mean)
    with pytest.raises(SeedDriftContractError, match="duplicate"):
        mod.assert_mi06_quick_run_reproduces(seed=42)