"""MI.TARGET.LEAKAGE — ST-ML-02 MI-15 offline (oneshot-c173)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from labcore.integrity.target_leakage_contract import (
    ARTEFACT_ID,
    TargetLeakageContractError,
    assert_mi15_intake_excludes_critical_leak,
    assert_mi15_near_perfect_predictor,
    assert_mi15_post_outcome_name,
    assert_target_leakage_contract,
    target_leakage_manifest,
)
from labcore.intake.d6_leakage import detect_leakage
from labcore.intake.profile import extended_profile


def test_target_leakage_contract_bundle() -> None:
    checks = assert_target_leakage_contract(seed=42)
    assert len(checks) == 3


def test_mi15_near_perfect_predictor() -> None:
    out = assert_mi15_near_perfect_predictor(seed=42)
    assert out["mi_rule"] == "MI-15"
    assert out["rule"] == "near_perfect_predictor"


def test_mi15_post_outcome_name() -> None:
    out = assert_mi15_post_outcome_name(seed=42)
    assert out["rule"] == "post_outcome_name"


def test_mi15_intake_excludes_critical() -> None:
    assert_mi15_intake_excludes_critical_leak(seed=42)


def test_manifest_seed_42() -> None:
    manifest = target_leakage_manifest(seed=42)
    assert manifest["id"] == ARTEFACT_ID
    assert manifest["seed"] == 42
    assert manifest["stress_test"] == "ST-ML-02"
    assert manifest["mi_rule"] == "MI-15"


def test_mi15_negative_no_flag_on_benign_feature(monkeypatch: pytest.MonkeyPatch) -> None:
    import labcore.integrity.target_leakage_contract as mod

    def noop(*_a, **_k):
        return []

    monkeypatch.setattr(mod, "detect_leakage", noop)
    with pytest.raises(TargetLeakageContractError, match="MI-15"):
        mod.assert_mi15_near_perfect_predictor(seed=42)


def test_mi15_detector_benign_noise_not_critical() -> None:
    rng = np.random.default_rng(42)
    n = 200
    y = rng.integers(0, 2, size=n)
    df = pd.DataFrame({"y": y, "noise": rng.normal(size=n)})
    profile = extended_profile(df)
    roles = {c: {"role": "feature", "included": True} for c in df.columns if c != "y"}
    roles["y"] = {"role": "target", "included": True}
    suspects = detect_leakage(
        df,
        profile,
        roles,
        [{"column": "y"}],
        {},
        {"proposed": "supervised_non_sequential"},
    )
    critical = [s for s in suspects if s.get("column") == "noise" and s.get("severity") == "critical"]
    assert not critical