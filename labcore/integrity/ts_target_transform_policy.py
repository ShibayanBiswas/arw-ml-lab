"""TS target transform scope — MI-05 (ARCHITECTURE §46.1).

Box-Cox λ (and similar) must be estimated on each backtest window's training
history only, not on the full series or on rows that include the window's test
segment.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from sklearn.preprocessing import PowerTransformer

MI05_RULE = "MI-05"
DEFAULT_BACKTEST_WINDOWS = 4
DEFAULT_HORIZON = 8
MIN_TRAIN_ROWS = 30
LAMBDA_ATOL = 1e-4


def fit_boxcox_lambda(y: np.ndarray) -> float:
    """Return Box-Cox λ from sklearn ``PowerTransformer`` fit on ``y`` only."""
    y_pos = np.asarray(y, dtype=float).ravel()
    if y_pos.size == 0:
        raise ValueError("y must be non-empty")
    if np.any(y_pos <= 0):
        raise ValueError("Box-Cox requires strictly positive targets")
    pt = PowerTransformer(method="box-cox", standardize=False)
    pt.fit(y_pos.reshape(-1, 1))
    return float(pt.lambdas_[0])


def full_pre_holdout_slice(y: np.ndarray, *, horizon: int) -> np.ndarray:
    """Training history before the final holdout block of length ``horizon``."""
    if len(y) <= horizon:
        raise ValueError("series shorter than holdout horizon")
    return np.asarray(y[: len(y) - horizon], dtype=float)


def expanding_backtest_train_slices(
    y: np.ndarray,
    *,
    n_windows: int = DEFAULT_BACKTEST_WINDOWS,
    horizon: int = DEFAULT_HORIZON,
    min_train: int = MIN_TRAIN_ROWS,
) -> list[np.ndarray]:
    """Expanding training targets for each backtest origin (history-only rows)."""
    y_arr = np.asarray(y, dtype=float).ravel()
    n = len(y_arr)
    if n < min_train + horizon:
        raise ValueError("series too short for backtest windows")
    last_train_end = n - horizon
    first_train_end = min_train
    if n_windows <= 1:
        return [y_arr[:last_train_end]]
    step = max(1, (last_train_end - first_train_end) // (n_windows - 1))
    ends = [min(first_train_end + i * step, last_train_end) for i in range(n_windows)]
    ends[-1] = last_train_end
    return [y_arr[:end] for end in ends]


def lambdas_per_backtest_window(
    y: np.ndarray,
    *,
    n_windows: int = DEFAULT_BACKTEST_WINDOWS,
    horizon: int = DEFAULT_HORIZON,
    min_train: int = MIN_TRAIN_ROWS,
) -> list[float]:
    """Box-Cox λ fitted independently on each backtest training slice."""
    slices = expanding_backtest_train_slices(
        y,
        n_windows=n_windows,
        horizon=horizon,
        min_train=min_train,
    )
    return [fit_boxcox_lambda(s) for s in slices]


def lambdas_differ(lambdas: Sequence[float], *, atol: float = LAMBDA_ATOL) -> bool:
    """True when at least two window λ values differ beyond ``atol``."""
    if len(lambdas) < 2:
        return False
    rounded = [round(float(lam), 4) for lam in lambdas]
    return len(set(rounded)) > 1 or max(lambdas) - min(lambdas) > atol


def lambda_close(a: float, b: float, *, atol: float = LAMBDA_ATOL) -> bool:
    return abs(float(a) - float(b)) <= atol


def make_mi05_skew_shift_fixture(*, seed: int = 42, n: int = 104) -> np.ndarray:
    """Positive series with a mid-series skew shift so early λ ≠ late λ."""
    rng = np.random.default_rng(seed)
    split = n // 2
    low = 1.0 + rng.lognormal(mean=0.0, sigma=0.25, size=split)
    high = 1.0 + rng.lognormal(mean=0.0, sigma=1.15, size=n - split)
    return np.concatenate([low, high], dtype=float)