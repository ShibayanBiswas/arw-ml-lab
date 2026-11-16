"""Purged K-Fold + CPCV unit tests (seed 42)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from labcore.cv import CombinatorialPurgedKFold, PurgedKFold, build_splitter, ml_get_train_times


def test_ml_get_train_times_drops_overlap():
    t1 = pd.Series([2, 3, 4, 5, 6], index=[0, 1, 2, 3, 4])
    test_times = pd.Series([4], index=[2])  # test sample at 2 ends at 4
    train = ml_get_train_times(t1, test_times)
    assert 2 not in train.index
    # sample 1 ends at 3 which is inside [2,4] → purged
    assert 1 not in train.index


def test_purged_kfold_no_train_test_index_overlap():
    X = np.arange(100).reshape(-1, 1)
    cv = PurgedKFold(n_splits=5, pct_embargo=0.02)
    for train_idx, test_idx in cv.split(X):
        assert len(np.intersect1d(train_idx, test_idx)) == 0
        assert len(test_idx) > 0
        assert len(train_idx) > 0


def test_purged_kfold_with_label_horizon():
    n = 80
    # each label spans 5 bars ahead
    t1 = pd.Series(np.arange(n) + 5, index=np.arange(n))
    X = np.random.default_rng(42).normal(size=(n, 2))
    cv = PurgedKFold(n_splits=4, samples_info_sets=t1, pct_embargo=0.01)
    for train_idx, test_idx in cv.split(X):
        assert len(np.intersect1d(train_idx, test_idx)) == 0


def test_cpcv_split_count_and_paths():
    X = np.arange(60).reshape(-1, 1)
    cv = CombinatorialPurgedKFold(n_splits=6, n_test_splits=2, pct_embargo=0.01)
    splits = list(cv.split(X))
    assert len(splits) == cv.get_n_splits()
    paths = cv.backtest_paths(len(X))
    assert len(paths) >= 1
    assert all(len(p) == len(X) for p in paths)


def test_build_splitter_purged_and_cpcv():
    pk = build_splitter("purged_kfold", n_splits=3, pct_embargo=0.01)
    assert isinstance(pk, PurgedKFold)
    cp = build_splitter("cpcv", n_splits=5, n_test_splits=2)
    assert isinstance(cp, CombinatorialPurgedKFold)
