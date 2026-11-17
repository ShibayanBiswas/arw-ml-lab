"""Pipeline fit-scope checks — MI-01 (ARCHITECTURE §46.1).

Preprocessing must be fitted only on each CV fold's training rows via a single
``sklearn.pipeline.Pipeline`` passed to ``cross_validate`` / fold loops — never
``fit_transform`` on the full frame before splitting.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

MI01_RULE = "MI-01"


class FitIndexSpy(BaseEstimator, TransformerMixin):
    """Records ``fit`` row indices for MI-01 leakage checks."""

    def __init__(self) -> None:
        self.fit_indices_: np.ndarray | None = None

    def fit(self, X: pd.DataFrame | np.ndarray, y: object | None = None) -> FitIndexSpy:
        if isinstance(X, pd.DataFrame):
            self.fit_indices_ = np.asarray(X.index)
        else:
            self.fit_indices_ = np.arange(len(X))
        return self

    def transform(self, X: pd.DataFrame | np.ndarray) -> pd.DataFrame | np.ndarray:
        return X


def fit_indices_match_train(
    fit_indices: np.ndarray,
    train_idx: np.ndarray,
    *,
    index: pd.Index | None = None,
) -> bool:
    """True when spy indices equal the fold train positions (or index labels)."""
    if index is not None:
        expected = np.asarray(index.take(train_idx))
    else:
        expected = np.asarray(train_idx, dtype=int)
    if fit_indices.shape != expected.shape:
        return False
    return bool(np.array_equal(np.sort(fit_indices), np.sort(expected)))


def full_frame_prefit_violates_mi01(n_fit: int, n_rows: int, *, n_splits: int) -> bool:
    """Heuristic: fitting on all rows before CV implies spy length == n_rows, not train size."""
    if n_fit != n_rows:
        return False
    # train fraction for KFold ~ (n_splits - 1) / n_splits
    min_train = (n_splits - 1) * n_rows // n_splits
    return n_fit > min_train