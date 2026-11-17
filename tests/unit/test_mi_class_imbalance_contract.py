"""MI.CLASS.RESAMPLE — ST-ML-02 MI-07 offline (oneshot-c170)."""

from __future__ import annotations

import pytest

from labcore.integrity.class_imbalance_contract import (
    ARTEFACT_ID,
    ClassImbalanceContractError,
    assert_mi07_imbalance_detection,
    assert_mi07_recipe_wires_smote,
    assert_mi07_smote_resampler_fold_train_only,
    class_imbalance_manifest,
)
from labcore.integrity.class_imbalance_policy import MI07_RULE


def test_mi07_imbalance_detection():
    out = assert_mi07_imbalance_detection(seed=42)
    assert out["mi_rule"] == MI07_RULE
    assert out["extreme_rarity"] is True
    assert out["balanced_ok"] is True


def test_mi07_smote_fold_train_only():
    out = assert_mi07_smote_resampler_fold_train_only(seed=42)
    assert out["folds_verified"] == 4
    assert out["resample"] == "smote"


def test_mi07_recipe_smote():
    out = assert_mi07_recipe_wires_smote(seed=42)
    assert out["resample_class"] == "SMOTE"


def test_class_imbalance_manifest():
    m = class_imbalance_manifest(seed=42)
    assert m["id"] == ARTEFACT_ID
    assert m["stress_test"] == "ST-ML-02"
    assert len(m["checks"]) == 3


def test_contract_raises_when_spy_mismatch(monkeypatch: pytest.MonkeyPatch):
    from labcore.integrity import class_imbalance_contract as mod

    def broken(*, seed: int = 42) -> dict[str, object]:
        raise ClassImbalanceContractError("MI-07: resampler pipeline fit must see train rows only")

    monkeypatch.setattr(mod, "assert_mi07_smote_resampler_fold_train_only", broken)
    with pytest.raises(ClassImbalanceContractError, match="train rows only"):
        mod.assert_class_imbalance_contract(seed=42)