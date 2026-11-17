"""MI.PURGED.SPLIT — ST-ML-02 MI-04 offline (oneshot-c168)."""

from __future__ import annotations

import numpy as np
import pytest

from labcore.cv.purged import PurgedKFold
from labcore.integrity.purged_split_contract import (
    ARTEFACT_ID,
    PurgedSplitContractError,
    assert_mi04_cpcv_no_label_overlap,
    assert_mi04_naive_split_leaks,
    assert_mi04_purged_kfold_no_label_overlap,
    purged_split_manifest,
)
from labcore.integrity.purged_split_policy import (
    MI04_RULE,
    fold_has_no_label_overlap,
    label_interval_overlaps,
    make_mi04_horizon_fixture,
    fold_test_block_contiguous,
)


def test_label_interval_overlaps_helper():
    assert label_interval_overlaps(2, 6, 5, 8)
    assert not label_interval_overlaps(0, 2, 5, 8)


def test_contiguous_sequential_helper():
    assert fold_test_block_contiguous(np.array([10, 11, 12]))
    assert not fold_test_block_contiguous(np.array([10, 12, 13]))


def test_mi04_purged_kfold_no_label_overlap():
    out = assert_mi04_purged_kfold_no_label_overlap(seed=42)
    assert out["mi_rule"] == MI04_RULE
    assert out["folds_verified"] == 4


def test_mi04_cpcv_no_label_overlap():
    out = assert_mi04_cpcv_no_label_overlap(seed=42)
    assert out["splits_verified"] >= 1


def test_mi04_naive_split_leaks():
    out = assert_mi04_naive_split_leaks(seed=42)
    assert out["naive_leak_detected"] is True


def test_purged_split_manifest():
    m = purged_split_manifest(seed=42)
    assert m["id"] == ARTEFACT_ID
    assert m["stress_test"] == "ST-ML-02"
    assert len(m["checks"]) == 3


def test_contract_raises_when_overlap_slips(monkeypatch: pytest.MonkeyPatch):
    from labcore.integrity import purged_split_contract as mod

    monkeypatch.setattr(mod, "fold_has_no_label_overlap", lambda *a, **k: True)
    with pytest.raises(PurgedSplitContractError, match="naive"):
        mod.assert_mi04_naive_split_leaks(seed=42)


def test_horizon_fixture_matches_purged_splits():
    t1 = make_mi04_horizon_fixture(seed=42)
    X = np.zeros((len(t1), 1))
    cv = PurgedKFold(n_splits=4, samples_info_sets=t1, pct_embargo=0.02)
    for train_idx, test_idx in cv.split(X):
        assert fold_has_no_label_overlap(train_idx, test_idx, t1)
        assert len(np.intersect1d(train_idx, test_idx)) == 0