"""MI.HIGH.CARD — ST-ML-02 MI-10 offline (oneshot-c172)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from labcore.integrity.high_cardinality_contract import (
    ARTEFACT_ID,
    HighCardinalityContractError,
    assert_high_cardinality_contract,
    high_cardinality_manifest,
)
from labcore.integrity.high_cardinality_policy import (
    HIGH_CARDINALITY_LEVELS,
    ONE_HOT_MAX_LEVELS,
    propose_categorical_encoders,
)


def test_repo_high_cardinality_contract() -> None:
    checks = assert_high_cardinality_contract(seed=42)
    assert len(checks) == 4


def test_propose_encoders_thresholds() -> None:
    assert propose_categorical_encoders(HIGH_CARDINALITY_LEVELS + 1) == [
        "target",
        "hashing",
        "count",
    ]
    assert propose_categorical_encoders(ONE_HOT_MAX_LEVELS + 1) == ["one_hot"]


def test_manifest_seed_42() -> None:
    manifest = high_cardinality_manifest(seed=42)
    assert manifest["id"] == ARTEFACT_ID
    assert manifest["seed"] == 42
    assert manifest["stress_test"] == "ST-ML-02"


def test_mi10_proposals_negative(monkeypatch: pytest.MonkeyPatch) -> None:
    import labcore.integrity.high_cardinality_contract as mod

    monkeypatch.setattr(
        mod,
        "propose_categorical_encoders",
        lambda _n: ["one_hot"],
    )
    with pytest.raises(HighCardinalityContractError, match="MI-10"):
        mod.assert_mi10_encoder_proposals_above_50(seed=42)


def test_mi10_onehot_cap_negative(monkeypatch: pytest.MonkeyPatch) -> None:
    import labcore.integrity.high_cardinality_contract as mod

    monkeypatch.setattr(
        mod,
        "one_hot_output_within_cap",
        lambda *a, **k: {"within_cap": False, "n_output_features": 999, "n_levels": 55},
    )
    with pytest.raises(HighCardinalityContractError, match="MI-10"):
        mod.assert_mi10_onehot_capped_at_30(seed=42)