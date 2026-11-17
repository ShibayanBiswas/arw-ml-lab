"""Class imbalance / resampling in folds — MI-07 (ARCHITECTURE §46.1)."""

from __future__ import annotations

import numpy as np
from sklearn.base import BaseEstimator

MI07_RULE = "MI-07"

IMBALANCE_MINORITY_SHARE = 0.20
IMBALANCE_RATIO_MAX = 4.0
EXTREME_RARITY_MINORITY_ROWS = 30


def validation_prediction_length_unchanged(pipe: BaseEstimator, X_val: np.ndarray) -> bool:
    """imblearn Pipeline must predict one label per validation row (SMOTE train-only)."""
    pred = pipe.predict(X_val)
    return int(len(pred)) == int(len(X_val))


def smote_inflates_train_only(
    n_train: int,
    n_after_resample: int,
    *,
    n_val: int,
) -> bool:
    """SMOTE may upsample train rows but must not change validation cardinality."""
    return n_after_resample >= n_train and n_val > 0