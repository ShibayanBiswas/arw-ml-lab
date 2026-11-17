"""SEC.FEATURE_CONTRACT.IDENTIFIER — §45.2 identifier value ban (oneshot-c158)."""

from __future__ import annotations

import pytest

from labcore.predict.contract import build_feature_contract
from labcore.predict.identifier_ban_contract import (
    ARTEFACT_ID,
    IdentifierBanContractError,
    assert_identifier_ban_on_contract,
    identifier_ban_manifest,
    scan_predict_manifest_contracts,
)

import pandas as pd


def test_build_contract_passes_ban() -> None:
    df = pd.DataFrame({"name": [f"n{i}" for i in range(60)], "y": [0, 1] * 30})
    contract = build_feature_contract(df, dataset_id="T", task="binary", target="y", seed=42)
    assert_identifier_ban_on_contract(contract)


def test_rejects_stored_categories_on_identifier() -> None:
    bad = {
        "contract_version": "1.0",
        "dataset_id": "X",
        "task": "binary",
        "seed": 42,
        "features": [
            {"name": "ticket", "kind": "identifier_like", "categories": ["A-1", "B-2"]},
        ],
    }
    with pytest.raises(IdentifierBanContractError, match="categories"):
        assert_identifier_ban_on_contract(bad)


def test_kit_predict_contracts_scan() -> None:
    checked = scan_predict_manifest_contracts()
    assert len(checked) >= 30


def test_manifest_seed_42() -> None:
    manifest = identifier_ban_manifest(seed=42)
    assert manifest["id"] == ARTEFACT_ID
    assert manifest["seed"] == 42
    assert manifest["contracts_checked"]