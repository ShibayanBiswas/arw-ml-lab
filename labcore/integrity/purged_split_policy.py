"""Purged sequential / financial splits — MI-04 (ARCHITECTURE §46.1).

Uses ``labcore.cv.purged`` (AFML thin wrappers). Seed **42** on synthetic fixtures only.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

MI04_RULE = "MI-04"
DEFAULT_LABEL_HORIZON = 5


def label_interval_overlaps(
    train_start: int,
    train_end: int,
    test_start: int,
    test_end: int,
) -> bool:
    """True when train label span [train_start, train_end] overlaps test [test_start, test_end]."""
    return (
        (train_start >= test_start and train_start <= test_end)
        or (train_end >= test_start and train_end <= test_end)
        or (train_start <= test_start and train_end >= test_end)
    )


def fold_has_no_label_overlap(
    train_idx: np.ndarray,
    test_idx: np.ndarray,
    t1: pd.Series,
) -> bool:
    """MI-04: no train row's label interval may overlap any test row's interval."""
    for i in train_idx:
        i0, i1 = int(i), int(t1.iloc[int(i)])
        for j in test_idx:
            j0, j1 = int(j), int(t1.iloc[int(j)])
            if label_interval_overlaps(i0, i1, j0, j1):
                return False
    return True


def fold_test_block_contiguous(test_idx: np.ndarray) -> bool:
    """Sequential CV: each test fold is one contiguous index block, ascending."""
    if len(test_idx) == 0:
        return False
    sorted_idx = np.sort(test_idx)
    if not np.array_equal(test_idx, sorted_idx):
        return False
    gaps = np.diff(sorted_idx)
    return bool((gaps == 1).all())


def embargo_zone_after_test(max_test: int, n: int, *, pct_embargo: float) -> range:
    """Integer index positions embargoed immediately after the test block."""
    embargo = int(np.ceil(pct_embargo * n))
    end = min(n - 1, max_test + embargo)
    if end <= max_test:
        return range(0)
    return range(max_test + 1, end + 1)


def embargo_indices_absent_from_train(
    train_idx: np.ndarray,
    test_idx: np.ndarray,
    n: int,
    *,
    pct_embargo: float,
) -> bool:
    """Embargo tail must not appear in train (extended test_times purge)."""
    if len(test_idx) == 0:
        return True
    zone = embargo_zone_after_test(int(test_idx.max()), n, pct_embargo=pct_embargo)
    train_set = set(int(x) for x in train_idx)
    return not any(z in train_set for z in zone)


def make_mi04_horizon_fixture(*, n: int = 96, horizon: int = DEFAULT_LABEL_HORIZON, seed: int = 42) -> pd.Series:
    """samples_info_sets: index → label end (t1) with fixed forward horizon."""
    rng = np.random.default_rng(seed)
    idx = pd.RangeIndex(n)
    # Staggered horizon so purging removes more than point labels on some folds.
    jitter = rng.integers(0, 2, size=n)
    ends = np.minimum(idx.to_numpy() + horizon + jitter, n - 1)
    return pd.Series(ends, index=idx)


def naive_non_purged_train_indices(test_idx: np.ndarray, n: int) -> np.ndarray:
    """Negative fixture: all non-test rows kept — violates MI-04 with horizon labels."""
    mask = np.ones(n, dtype=bool)
    mask[test_idx] = False
    return np.where(mask)[0]