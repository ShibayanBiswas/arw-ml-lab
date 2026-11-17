"""MI.TARGET.ENCODING — ST-ML-02 MI-02 offline (oneshot-c166)."""

from __future__ import annotations

import pytest

from labcore.integrity.target_encoding_contract import (
    ARTEFACT_ID,
    TargetEncodingContractError,
    assert_mi02_noise_column_near_chance,
    assert_mi02_recipe_wires_target_encoder,
    target_encoding_manifest,
)
from labcore.integrity.target_encoding_policy import (
    MI02_MAX_AUC_DEVIATION,
    MI02_RULE,
    MI02_SYNTHETIC_ROWS,
    auc_deviation_from_chance,
    noise_auc_passes_mi02,
    target_encoder_shuffle,
)


def test_auc_deviation_helpers():
    assert auc_deviation_from_chance(0.5) == 0.0
    assert noise_auc_passes_mi02(0.52)
    assert not noise_auc_passes_mi02(0.56)


def test_target_encoder_shuffle_policy():
    assert target_encoder_shuffle(sequential=False) is True
    assert target_encoder_shuffle(sequential=True) is False


def test_mi02_recipe_wires_target_encoder():
    out = assert_mi02_recipe_wires_target_encoder(seed=42)
    assert out["mi_rule"] == MI02_RULE
    assert out["categorical_encoder"] == "target"


def test_mi02_noise_column_near_chance():
    out = assert_mi02_noise_column_near_chance(seed=42)
    assert out["n_rows"] == MI02_SYNTHETIC_ROWS
    assert out["auc_deviation_from_chance"] < MI02_MAX_AUC_DEVIATION


def test_target_encoding_manifest():
    m = target_encoding_manifest(seed=42)
    assert m["id"] == ARTEFACT_ID
    assert m["stress_test"] == "ST-ML-02"
    assert len(m["checks"]) == 3


def test_contract_raises_when_auc_guard_tight(monkeypatch: pytest.MonkeyPatch):
    from labcore.integrity import target_encoding_contract as mod

    def always_fail(_auc: float, **_kw: object) -> bool:
        return False

    monkeypatch.setattr(mod, "noise_auc_passes_mi02", always_fail)
    with pytest.raises(TargetEncodingContractError, match="noise AUC"):
        mod.assert_mi02_noise_column_near_chance(seed=42)