"""MI.DATA.QUALITY — ST-ML-03 MI-11/MI-12 offline (oneshot-c161)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from labcore.integrity.data_quality_contract import (
    ARTEFACT_ID,
    DataQualityContractError,
    assert_data_quality_contract,
    assert_mi11_drops_constant_and_all_nan,
    assert_mi12_ambiguous_date_intake,
    assert_recipe_drop_constant_default,
    data_quality_manifest,
)
from labcore.preprocess.recipe import RecipeSpec, drop_constant_columns


def test_repo_data_quality_contract() -> None:
    checks = assert_data_quality_contract(seed=42)
    assert len(checks) == 3


def test_recipe_drop_constant_default() -> None:
    meta = assert_recipe_drop_constant_default()
    assert meta["drop_constant_default"] == "true"
    assert RecipeSpec().drop_constant is True


def test_mi11_drop_helpers_match_contract() -> None:
    assert_mi11_drops_constant_and_all_nan(seed=42)
    df = pd.DataFrame({"k": [1, 2], "nan_col": [np.nan, np.nan]})
    out, dropped = drop_constant_columns(df)
    assert dropped == ["nan_col"] and list(out.columns) == ["k"]


def test_mi12_ambiguous_date_contract() -> None:
    result = assert_mi12_ambiguous_date_intake(seed=42)
    assert result["mi_rule"] == "MI-12"
    assert result["ambiguous_via_question"] or result["ambiguous_format_flag"]


def test_manifest_seed_42() -> None:
    manifest = data_quality_manifest(seed=42)
    assert manifest["id"] == ARTEFACT_ID
    assert manifest["seed"] == 42
    assert manifest["stress_test"] == "ST-ML-03"


def test_mi11_rejects_bad_drop(monkeypatch: pytest.MonkeyPatch) -> None:
    import labcore.integrity.data_quality_contract as mod
    import labcore.preprocess.recipe as recipe_mod

    def bad_drop(_x: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
        return _x, []

    monkeypatch.setattr(recipe_mod, "drop_constant_columns", bad_drop)
    with pytest.raises(DataQualityContractError, match="MI-11"):
        mod.assert_mi11_drops_constant_and_all_nan(seed=42)