"""MI.DUPLICATE.GROUP — ST-ML-02 MI-18 offline (oneshot-c164)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from labcore.integrity.duplicate_split_contract import (
    ARTEFACT_ID,
    DuplicateSplitContractError,
    assert_duplicate_split_contract,
    duplicate_split_manifest,
)
from labcore.integrity.duplicate_split_policy import (
    duplicate_group_labels,
    exact_duplicate_row_share,
    requires_duplicate_group_cv,
)


def test_repo_duplicate_split_contract() -> None:
    checks = assert_duplicate_split_contract(seed=42)
    assert len(checks) == 2


def test_duplicate_share_threshold() -> None:
    df = pd.DataFrame({"a": [1, 1, 2, 3, 4, 5]})
    assert exact_duplicate_row_share(df) > 0.0
    assert not requires_duplicate_group_cv(pd.DataFrame({"a": range(200)}))


def test_duplicate_groups_stable() -> None:
    df = pd.DataFrame({"a": [1, 1, 2]})
    g = duplicate_group_labels(df)
    assert int(g.iloc[0]) == int(g.iloc[1])


def test_manifest_seed_42() -> None:
    manifest = duplicate_split_manifest(seed=42)
    assert manifest["id"] == ARTEFACT_ID
    assert manifest["seed"] == 42


def test_mi18_threshold_negative(monkeypatch: pytest.MonkeyPatch) -> None:
    import labcore.integrity.duplicate_split_contract as mod

    monkeypatch.setattr(mod, "requires_duplicate_group_cv", lambda _df: False)
    with pytest.raises(DuplicateSplitContractError, match="MI-18"):
        mod.assert_mi18_threshold_gate(seed=42)