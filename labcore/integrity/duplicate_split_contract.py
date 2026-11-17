"""Duplicate rows across splits — MI-18 / ST-ML-02 (ARCHITECTURE §46.1)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold

from labcore.integrity.duplicate_split_policy import (
    DUPLICATE_GROUP_THRESHOLD,
    MI18_RULE,
    assert_groups_do_not_straddle_splits,
    duplicate_group_labels,
    mi18_split_recommendation,
    requires_duplicate_group_cv,
)

ARTEFACT_ID = "MI.DUPLICATE.GROUP"
STRESS_ID = "ST-ML-02"


class DuplicateSplitContractError(ValueError):
    """Raised when MI-18 offline kit contract is violated."""


def assert_mi18_threshold_gate(*, seed: int = 42) -> dict[str, object]:
    """MI-18: GroupKFold only when duplicate share > 1 %."""
    _ = seed
    clean = pd.DataFrame({"a": range(100), "b": range(100)})
    dirty = pd.concat([clean, clean.iloc[:5]], ignore_index=True)
    if requires_duplicate_group_cv(clean):
        raise DuplicateSplitContractError("MI-18: clean frame must not require group CV")
    if not requires_duplicate_group_cv(dirty):
        raise DuplicateSplitContractError("MI-18: >1% dupes must require group CV")
    rec = mi18_split_recommendation(dirty)
    if rec["recommended_cv_scheme"] != "group_kfold":
        raise DuplicateSplitContractError("MI-18: expected group_kfold recommendation")
    return {
        "mi_rule": MI18_RULE,
        "threshold": DUPLICATE_GROUP_THRESHOLD,
        "dirty_duplicate_share": rec["duplicate_row_share"],
        "seed": seed,
    }


def assert_mi18_group_kfold_no_leak(*, seed: int = 42) -> dict[str, object]:
    """MI-18: sklearn GroupKFold keeps duplicate groups wholly in train or test."""
    rng = np.random.default_rng(seed)
    base = pd.DataFrame({"x": rng.normal(size=40), "tag": ["A"] * 20 + ["B"] * 20})
    dupes = pd.concat([base, base.iloc[:8]], ignore_index=True)
    groups = duplicate_group_labels(dupes)
    gkf = GroupKFold(n_splits=4)
    for tr, te in gkf.split(dupes, groups=groups):
        try:
            assert_groups_do_not_straddle_splits(tr, te, groups)
        except ValueError as exc:
            raise DuplicateSplitContractError(str(exc)) from exc
    naive = __import__("sklearn.model_selection", fromlist=["KFold"]).KFold(
        n_splits=4, shuffle=True, random_state=seed,
    )
    leaked = False
    for tr, te in naive.split(dupes):
        g_tr = set(int(groups.iloc[i]) for i in tr)
        g_te = set(int(groups.iloc[i]) for i in te)
        if g_tr & g_te:
            leaked = True
            break
    if not leaked:
        raise DuplicateSplitContractError("MI-18: naive KFold should leak duplicate groups on fixture")
    return {
        "mi_rule": MI18_RULE,
        "n_rows": len(dupes),
        "n_groups": int(groups.nunique()),
        "group_kfold_verified": True,
        "seed": seed,
    }


def assert_duplicate_split_contract(*, seed: int = 42) -> list[dict[str, object]]:
    return [
        assert_mi18_threshold_gate(seed=seed),
        assert_mi18_group_kfold_no_leak(seed=seed),
    ]


def duplicate_split_manifest(*, seed: int = 42) -> dict[str, object]:
    checks = assert_duplicate_split_contract(seed=seed)
    return {
        "id": ARTEFACT_ID,
        "stress_test": STRESS_ID,
        "mi_rule": MI18_RULE,
        "seed": seed,
        "checks": checks,
    }