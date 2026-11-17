"""Duplicate-row grouping for CV — MI-18 (ARCHITECTURE §46.1).

When exact-duplicate rows exceed 1 % of the frame, splits must keep duplicate
groups intact (``GroupKFold`` on a stable row hash).
"""

from __future__ import annotations

import hashlib
from typing import Any

import numpy as np
import pandas as pd

DUPLICATE_GROUP_THRESHOLD = 0.01
MI18_RULE = "MI-18"


def exact_duplicate_row_share(df: pd.DataFrame) -> float:
    """Share of rows that participate in at least one exact duplicate."""
    if len(df) == 0:
        return 0.0
    mask = df.duplicated(keep=False)
    return float(mask.mean())


def duplicate_group_labels(df: pd.DataFrame) -> pd.Series:
    """Stable integer group id per row from a hash of row values."""
    if len(df) == 0:
        return pd.Series(dtype=int)
    labels: list[int] = []
    mapping: dict[str, int] = {}
    next_id = 0
    for row in df.itertuples(index=False, name=None):
        key = hashlib.sha256(repr(row).encode("utf-8")).hexdigest()
        gid = mapping.get(key)
        if gid is None:
            gid = next_id
            mapping[key] = gid
            next_id += 1
        labels.append(gid)
    return pd.Series(labels, index=df.index, dtype=int)


def requires_duplicate_group_cv(df: pd.DataFrame, *, threshold: float = DUPLICATE_GROUP_THRESHOLD) -> bool:
    """True when duplicate share strictly exceeds ``threshold`` (default 1 %)."""
    return exact_duplicate_row_share(df) > threshold


def assert_groups_do_not_straddle_splits(
    train_idx: np.ndarray,
    test_idx: np.ndarray,
    group_labels: pd.Series,
) -> None:
    """Raise if any duplicate group appears in both train and validation/test."""
    g_tr = set(int(group_labels.iloc[i]) for i in train_idx)
    g_te = set(int(group_labels.iloc[i]) for i in test_idx)
    leak = g_tr & g_te
    if leak:
        msg = f"duplicate groups leak across split: {sorted(leak)[:5]}"
        raise ValueError(msg)


def mi18_split_recommendation(df: pd.DataFrame) -> dict[str, Any]:
    """Summarise MI-18 policy for a frame (offline artefact numbers)."""
    share = exact_duplicate_row_share(df)
    groups = duplicate_group_labels(df)
    n_groups = int(groups.nunique()) if len(groups) else 0
    use_group_kfold = requires_duplicate_group_cv(df)
    return {
        "mi_rule": MI18_RULE,
        "duplicate_row_share": share,
        "n_rows": len(df),
        "n_duplicate_groups": n_groups,
        "use_group_kfold": use_group_kfold,
        "threshold": DUPLICATE_GROUP_THRESHOLD,
        "recommended_cv_scheme": "group_kfold" if use_group_kfold else None,
    }