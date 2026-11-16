"""Purged K-Fold and Combinatorial Purged CV (CPCV).

Implements López de Prado *Advances in Financial Machine Learning* ch. 7 / 12
without TradingLab (submodule not vendored yet). Keep under thin-wrapper budget;
parity tests vs AFML snippets live in ``tests/unit/test_purged_cv.py``.
"""

from __future__ import annotations

from collections.abc import Iterator
from itertools import combinations
from typing import Any

import numpy as np
import pandas as pd


def ml_get_train_times(
    samples_info_sets: pd.Series,
    test_times: pd.Series,
) -> pd.Series:
    """Drop train samples whose label interval overlaps any test interval (AFML 7.1).

    ``samples_info_sets`` maps sample start time → label end time (t1).
    ``test_times`` maps test-start → test-end (or a Series of test ends indexed by start).
    Returns the filtered ``samples_info_sets`` (train-eligible).
    """
    if samples_info_sets.empty:
        return samples_info_sets.copy()
    train = samples_info_sets.copy()
    for t0, t1 in test_times.items():
        # (a) starts inside test, (b) ends inside, (c) envelops test
        drop = (
            ((train.index >= t0) & (train.index <= t1))
            | ((train >= t0) & (train <= t1))
            | ((train.index <= t0) & (train >= t1))
        )
        train = train.loc[~drop]
    return train


def _as_t1_series(n: int, t1: pd.Series | np.ndarray | None) -> pd.Series:
    """Build samples_info_sets indexed by integer positions 0..n-1."""
    idx = pd.RangeIndex(n)
    if t1 is None:
        # point labels: t1 == t0
        return pd.Series(idx, index=idx)
    t1_arr = np.asarray(t1).ravel()
    if len(t1_arr) != n:
        raise ValueError(f"t1 length {len(t1_arr)} != n={n}")
    return pd.Series(t1_arr, index=idx)


class PurgedKFold:
    """Contiguous purged K-fold with embargo (AFML 7.2 / 7.3).

    Parameters
    ----------
    n_splits :
        Number of contiguous test folds.
    samples_info_sets :
        Optional Series mapping sample index → label end time. Defaults to
        point labels (t1 = index).
    pct_embargo :
        Fraction of the series length embargoed after each test fold.
    """

    def __init__(
        self,
        n_splits: int = 5,
        samples_info_sets: pd.Series | None = None,
        pct_embargo: float = 0.01,
    ) -> None:
        if n_splits < 2:
            raise ValueError("n_splits must be >= 2")
        self.n_splits = int(n_splits)
        self.samples_info_sets = samples_info_sets
        self.pct_embargo = float(pct_embargo)

    def get_n_splits(self, X: Any = None, y: Any = None, groups: Any = None) -> int:
        _ = (X, y, groups)
        return self.n_splits

    def split(
        self,
        X: Any,
        y: Any = None,
        groups: Any = None,
    ) -> Iterator[tuple[np.ndarray, np.ndarray]]:
        _ = (y, groups)
        n = len(X) if not hasattr(X, "shape") else int(X.shape[0])
        indices = np.arange(n)
        t1 = _as_t1_series(n, self.samples_info_sets)
        test_folds = np.array_split(indices, self.n_splits)
        embargo = int(np.ceil(self.pct_embargo * n))

        for test_idx in test_folds:
            if len(test_idx) == 0:
                continue
            test_times = pd.Series(
                [t1.iloc[i] for i in test_idx],
                index=[t1.index[i] for i in test_idx],
            )
            # Extend test times by embargo bars (on the integer index)
            max_test = int(test_idx.max())
            embargo_end = min(n - 1, max_test + embargo)
            if embargo_end > max_test:
                extra = list(range(max_test + 1, embargo_end + 1))
                for j in extra:
                    test_times.loc[t1.index[j]] = t1.iloc[j]

            train_t1 = ml_get_train_times(t1, test_times)
            train_idx = np.asarray(train_t1.index, dtype=int)
            # Never include test indices in train
            train_idx = np.setdiff1d(train_idx, test_idx, assume_unique=False)
            yield train_idx, np.asarray(test_idx, dtype=int)


class CombinatorialPurgedKFold:
    """Combinatorial Purged CV (AFML ch. 12).

    Splits into ``n_splits`` contiguous groups; every combination of
    ``n_test_splits`` groups forms a test set. Yields purged+embargoed
    train/test index pairs. ``backtest_paths`` stitches OOS assignments
    into φ paths for path-Sharpe distributions.
    """

    def __init__(
        self,
        n_splits: int = 6,
        n_test_splits: int = 2,
        samples_info_sets: pd.Series | None = None,
        pct_embargo: float = 0.01,
    ) -> None:
        if n_splits < 2:
            raise ValueError("n_splits must be >= 2")
        if not (1 <= n_test_splits < n_splits):
            raise ValueError("n_test_splits must be in [1, n_splits)")
        self.n_splits = int(n_splits)
        self.n_test_splits = int(n_test_splits)
        self.samples_info_sets = samples_info_sets
        self.pct_embargo = float(pct_embargo)

    def get_n_splits(self, X: Any = None, y: Any = None, groups: Any = None) -> int:
        _ = (X, y, groups)
        from math import comb

        return int(comb(self.n_splits, self.n_test_splits))

    def split(
        self,
        X: Any,
        y: Any = None,
        groups: Any = None,
    ) -> Iterator[tuple[np.ndarray, np.ndarray]]:
        _ = (y, groups)
        n = len(X) if not hasattr(X, "shape") else int(X.shape[0])
        indices = np.arange(n)
        groups_idx = np.array_split(indices, self.n_splits)
        t1 = _as_t1_series(n, self.samples_info_sets)
        embargo = int(np.ceil(self.pct_embargo * n))

        for test_group_ids in combinations(range(self.n_splits), self.n_test_splits):
            test_idx = np.concatenate([groups_idx[g] for g in test_group_ids])
            test_times = pd.Series(
                [t1.iloc[i] for i in test_idx],
                index=[t1.index[i] for i in test_idx],
            )
            max_test = int(test_idx.max())
            embargo_end = min(n - 1, max_test + embargo)
            if embargo_end > max_test:
                for j in range(max_test + 1, embargo_end + 1):
                    test_times.loc[t1.index[j]] = t1.iloc[j]
            train_t1 = ml_get_train_times(t1, test_times)
            train_idx = np.setdiff1d(
                np.asarray(train_t1.index, dtype=int),
                test_idx,
                assume_unique=False,
            )
            yield train_idx, np.asarray(test_idx, dtype=int)

    def backtest_paths(self, n_samples: int) -> list[list[int]]:
        """Return φ path assignments: for each path, the split-id covering each sample.

        Path stitching follows AFML: each sample appears in C(N-1, k-1) test sets;
        paths are built so each path covers the timeline without overlapping tests
        within a path. Simplified constructive version used for PBO/CPCV UI.
        """
        from math import comb

        groups_idx = np.array_split(np.arange(n_samples), self.n_splits)
        test_combos = list(combinations(range(self.n_splits), self.n_test_splits))
        n_paths = int(comb(self.n_splits - 1, self.n_test_splits - 1)) if self.n_test_splits else 1
        # Map each (group, path) → which combo covers it when that group is in test
        paths: list[list[int]] = [([-1] * n_samples) for _ in range(n_paths)]
        # Deterministic assignment: for each combo, assign to path by hash of remaining groups
        path_slots: dict[tuple[int, ...], int] = {}
        slot = 0
        for combo in test_combos:
            # key = sorted groups NOT in this combo's first test group context
            key = tuple(sorted(combo))
            # Assign combo to path index via round-robin on first test group
            g0 = combo[0]
            path_id = path_slots.get(combo)
            if path_id is None:
                path_id = (g0 + slot) % max(n_paths, 1)
                path_slots[combo] = path_id
                slot += 1
            for g in combo:
                for i in groups_idx[g]:
                    if paths[path_id][int(i)] < 0:
                        paths[path_id][int(i)] = test_combos.index(combo)
        return paths


def purged_fold_counts(
    train_idx: np.ndarray,
    test_idx: np.ndarray,
    n: int,
    *,
    pct_embargo: float,
) -> dict[str, int]:
    """Report n_train / n_test / n_purged / n_embargoed for the CV visualiser."""
    embargo = int(np.ceil(pct_embargo * n))
    all_idx = set(range(n))
    kept = set(train_idx.tolist()) | set(test_idx.tolist())
    purged = len(all_idx - kept) - embargo  # rough: non-embargo removals
    return {
        "n_train": int(len(train_idx)),
        "n_test": int(len(test_idx)),
        "n_purged": int(max(0, purged)),
        "n_embargoed": int(embargo),
    }
