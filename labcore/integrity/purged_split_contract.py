"""Purged K-fold / sequential splits — MI-04 / ST-ML-02 (ARCHITECTURE §46.1)."""

from __future__ import annotations

import numpy as np

from labcore.cv.purged import CombinatorialPurgedKFold, PurgedKFold
from labcore.integrity.purged_split_policy import (
    DEFAULT_LABEL_HORIZON,
    MI04_RULE,
    embargo_indices_absent_from_train,
    fold_has_no_label_overlap,
    make_mi04_horizon_fixture,
    naive_non_purged_train_indices,
    fold_test_block_contiguous,
)

ARTEFACT_ID = "MI.PURGED.SPLIT"
STRESS_ID = "ST-ML-02"
DEFAULT_N = 96
DEFAULT_SPLITS = 4
DEFAULT_EMBARGO = 0.02


class PurgedSplitContractError(ValueError):
    """Raised when MI-04 offline kit contract is violated."""


def assert_mi04_purged_kfold_no_label_overlap(*, seed: int = 42) -> dict[str, object]:
    """MI-04: PurgedKFold train sets have zero train/test label-interval overlap per fold."""
    t1 = make_mi04_horizon_fixture(n=DEFAULT_N, horizon=DEFAULT_LABEL_HORIZON, seed=seed)
    X = np.zeros((DEFAULT_N, 1))
    cv = PurgedKFold(
        n_splits=DEFAULT_SPLITS,
        samples_info_sets=t1,
        pct_embargo=DEFAULT_EMBARGO,
    )
    folds_ok = 0
    for train_idx, test_idx in cv.split(X):
        if not fold_test_block_contiguous(test_idx):
            raise PurgedSplitContractError("MI-04: purged test folds must be contiguous (no shuffle)")
        if not fold_has_no_label_overlap(train_idx, test_idx, t1):
            raise PurgedSplitContractError("MI-04: train label interval overlaps test")
        if not embargo_indices_absent_from_train(
            train_idx,
            test_idx,
            DEFAULT_N,
            pct_embargo=DEFAULT_EMBARGO,
        ):
            raise PurgedSplitContractError("MI-04: embargo tail must not be in train")
        folds_ok += 1
    if folds_ok != DEFAULT_SPLITS:
        raise PurgedSplitContractError(f"MI-04: expected {DEFAULT_SPLITS} folds, got {folds_ok}")
    return {
        "mi_rule": MI04_RULE,
        "splitter": "PurgedKFold",
        "n_rows": DEFAULT_N,
        "label_horizon": DEFAULT_LABEL_HORIZON,
        "folds_verified": folds_ok,
        "pct_embargo": DEFAULT_EMBARGO,
        "seed": seed,
    }


def assert_mi04_cpcv_no_label_overlap(*, seed: int = 42) -> dict[str, object]:
    """MI-04: CPCV combinatorial test blocks respect the same purge rule."""
    t1 = make_mi04_horizon_fixture(n=DEFAULT_N, horizon=DEFAULT_LABEL_HORIZON, seed=seed)
    X = np.zeros((DEFAULT_N, 1))
    cv = CombinatorialPurgedKFold(
        n_splits=6,
        n_test_splits=2,
        samples_info_sets=t1,
        pct_embargo=DEFAULT_EMBARGO,
    )
    verified = 0
    for train_idx, test_idx in cv.split(X):
        if not fold_has_no_label_overlap(train_idx, test_idx, t1):
            raise PurgedSplitContractError("MI-04: CPCV fold has label overlap")
        verified += 1
    if verified != cv.get_n_splits(X):
        raise PurgedSplitContractError("MI-04: CPCV split count mismatch")
    return {
        "mi_rule": MI04_RULE,
        "splitter": "CombinatorialPurgedKFold",
        "splits_verified": verified,
        "seed": seed,
    }


def assert_mi04_naive_split_leaks(*, seed: int = 42) -> dict[str, object]:
    """MI-04 negative: keeping all non-test rows leaks label overlap on horizon fixture."""
    t1 = make_mi04_horizon_fixture(n=DEFAULT_N, horizon=DEFAULT_LABEL_HORIZON, seed=seed)
    X = np.zeros((DEFAULT_N, 1))
    cv = PurgedKFold(n_splits=DEFAULT_SPLITS, samples_info_sets=t1, pct_embargo=0.0)
    _train, test_idx = next(iter(cv.split(X)))
    naive = naive_non_purged_train_indices(test_idx, DEFAULT_N)
    leaks = not fold_has_no_label_overlap(naive, test_idx, t1)
    if not leaks:
        raise PurgedSplitContractError("MI-04: naive non-purged split must leak on horizon fixture")
    return {
        "mi_rule": MI04_RULE,
        "naive_leak_detected": True,
        "n_naive_train": int(len(naive)),
        "n_test": int(len(test_idx)),
        "seed": seed,
    }


def assert_purged_split_contract(*, seed: int = 42) -> list[dict[str, object]]:
    return [
        assert_mi04_purged_kfold_no_label_overlap(seed=seed),
        assert_mi04_cpcv_no_label_overlap(seed=seed),
        assert_mi04_naive_split_leaks(seed=seed),
    ]


def purged_split_manifest(*, seed: int = 42) -> dict[str, object]:
    checks = assert_purged_split_contract(seed=seed)
    return {
        "id": ARTEFACT_ID,
        "stress_test": STRESS_ID,
        "mi_rule": MI04_RULE,
        "seed": seed,
        "checks": checks,
    }