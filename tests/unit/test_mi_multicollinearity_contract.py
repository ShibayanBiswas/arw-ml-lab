"""MI.MULTICOLLINEARITY — ST-ML-02 MI-14 offline (oneshot-c175)."""

from __future__ import annotations

import pytest

from labcore.integrity.multicollinearity_contract import (
    ARTEFACT_ID,
    MulticollinearityContractError,
    assert_multicollinearity_contract,
    multicollinearity_manifest,
)
from labcore.integrity.multicollinearity_policy import VIF_HIGH_THRESHOLD


def test_repo_multicollinearity_contract() -> None:
    checks = assert_multicollinearity_contract(seed=42)
    assert len(checks) == 3


def test_manifest_seed_42() -> None:
    manifest = multicollinearity_manifest(seed=42)
    assert manifest["id"] == ARTEFACT_ID
    assert manifest["seed"] == 42
    assert manifest["stress_test"] == "ST-ML-02"
    assert manifest["mi_rule"] == "MI-14"


def test_mi14_vif_negative(monkeypatch: pytest.MonkeyPatch) -> None:
    import labcore.integrity.multicollinearity_contract as mod

    monkeypatch.setattr(
        mod,
        "_vif_rows",
        lambda *_a, **_k: [
            {"feature": "x1", "vif": 2.0, "flag": "ok"},
            {"feature": "x2", "vif": 2.1, "flag": "ok"},
        ],
    )
    with pytest.raises(MulticollinearityContractError, match="MI-14"):
        mod.assert_mi14_high_vif_on_collinear_pair(seed=42)

    monkeypatch.setattr(
        mod,
        "_vif_rows",
        lambda *_a, **_k: [
            {"feature": "x1", "vif": VIF_HIGH_THRESHOLD + 5, "flag": "high"},
            {"feature": "x3", "vif": VIF_HIGH_THRESHOLD + 1, "flag": "high"},
        ],
    )
    with pytest.raises(MulticollinearityContractError, match="x3"):
        mod.assert_mi14_high_vif_on_collinear_pair(seed=42)