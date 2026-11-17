"""Run seed / reproducibility — MI-06 (ARCHITECTURE §46.1)."""

from __future__ import annotations

import random

import numpy as np

MI06_RULE = "MI-06"
LAB_DEFAULT_SEED = 42
METRIC_REPRODUCE_ATOL = 1e-12


def apply_lab_seed(seed: int = LAB_DEFAULT_SEED) -> None:
    """Central seed hook: numpy, stdlib random, torch/Lightning when installed."""
    random.seed(seed)
    np.random.seed(seed)
    try:
        from labcore.deep.engine import set_seed

        set_seed(seed)
    except ImportError:
        pass


def metrics_close(a: float, b: float, *, atol: float = METRIC_REPRODUCE_ATOL) -> bool:
    if not (np.isfinite(a) and np.isfinite(b)):
        return False
    return bool(abs(a - b) <= atol)


def metrics_differ(a: float, b: float, *, atol: float = METRIC_REPRODUCE_ATOL) -> bool:
    return not metrics_close(a, b, atol=atol)