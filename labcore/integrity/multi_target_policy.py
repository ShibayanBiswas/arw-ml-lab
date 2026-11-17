"""Multi-target supervised policy — MI-13 (ARCHITECTURE §46.1, §45)."""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.metrics import r2_score
from sklearn.multioutput import MultiOutputClassifier, MultiOutputRegressor, RegressorChain

MI13_RULE = "MI-13"
LAB_DEFAULT_SEED = 42


def wrap_multioutput_regressor(estimator: Any) -> MultiOutputRegressor:
    """MI-13: sklearn ``MultiOutputRegressor`` over a single-output base estimator."""
    return MultiOutputRegressor(estimator)


def wrap_regressor_chain(estimator: Any, *, random_state: int = LAB_DEFAULT_SEED) -> RegressorChain:
    """MI-13: ``RegressorChain`` with explicit ``random_state`` (chain order)."""
    return RegressorChain(estimator, random_state=random_state)


def wrap_multilabel_classifier(estimator: Any) -> MultiOutputClassifier:
    """MI-13: ``MultiOutputClassifier`` for multilabel Y ∈ {0,1}^{n×L}."""
    return MultiOutputClassifier(estimator)


def per_target_r2(
    y_true: np.ndarray,
    y_pred: np.ndarray,
) -> list[float]:
    """Per-column R² (``multioutput='raw_values'``); averaged via macro mean."""
    scores = r2_score(y_true, y_pred, multioutput="raw_values")
    return [float(v) for v in np.asarray(scores).ravel()]


def macro_mean_r2(per_target: list[float]) -> float:
    arr = np.asarray(per_target, dtype=float)
    if arr.size == 0:
        return float("nan")
    return float(np.mean(arr))


def prediction_studio_column_groups(
    target_names: list[str],
    *,
    suffix: str = "_pred",
) -> dict[str, list[str]]:
    """MI-13 / §45: one Prediction Studio column group per target."""
    return {name: [f"{name}{suffix}"] for name in target_names}