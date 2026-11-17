"""Sample-size policy — MI-07 / MI-08 / MI-09 (ARCHITECTURE §46.1, §39.3).

Thin helpers for small/large data behaviour (ST-ML-05); callers enqueue/train
layers use these for gating and refusal messages with concrete numbers.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Literal

import numpy as np

from labcore.cv.schemes import CV_SCHEME_IDS, default_scheme_for_task

if TYPE_CHECKING:
    from labcore.registry.spec import AlgorithmSpec

SMALL_N_REPEATED_CV = 200
LOO_N_THRESHOLD = 50
DL_MIN_ROWS_DEFAULT = 1000
EXTREME_RARITY_MINORITY_ROWS = 30
IMBALANCE_MINORITY_SHARE = 0.20
IMBALANCE_RATIO_MAX = 4.0
BYTES_PER_CELL = 8
REFUSAL_OVER_LIMIT_RATIO = 1.2

TaskKind = Literal["binary", "multiclass", "regression"]


def cv_scheme_for_n(n_train: int, task: str = "binary") -> str:
    """MI-08: repeated CV when n < 200; LOO when n < 50."""
    if n_train < LOO_N_THRESHOLD:
        return "leave_one_out"
    if n_train < SMALL_N_REPEATED_CV:
        return "repeated_stratified_kfold" if task != "regression" else "repeated_kfold"
    return default_scheme_for_task(task)


def classify_class_imbalance(y: Sequence[Any] | np.ndarray) -> dict[str, Any]:
    """MI-07: flag imbalance when minority share < 20 % or majority/minority > 4."""
    arr = np.asarray(y)
    if arr.size == 0:
        raise ValueError("y must be non-empty")
    _uniq, counts = np.unique(arr, return_counts=True)
    total = int(counts.sum())
    minority_count = int(counts.min())
    majority_count = int(counts.max())
    minority_share = minority_count / total if total else 0.0
    ratio = (majority_count / minority_count) if minority_count > 0 else float("inf")
    imbalanced = minority_share < IMBALANCE_MINORITY_SHARE or ratio > IMBALANCE_RATIO_MAX
    extreme_rarity = minority_count < EXTREME_RARITY_MINORITY_ROWS
    return {
        "n": total,
        "minority_count": minority_count,
        "minority_share": float(minority_share),
        "imbalance_ratio": float(ratio),
        "imbalanced": imbalanced,
        "extreme_rarity": extreme_rarity,
        "recommend_repeated_stratified_cv": extreme_rarity,
    }


def _is_deep_spec(spec: "AlgorithmSpec") -> bool:
    tags = {t.lower() for t in spec.tags}
    if "deep" in tags or "dl" in tags:
        return True
    return spec.key.startswith("dl.")


def eligible_algorithms(
    n_rows: int,
    specs: Sequence["AlgorithmSpec"],
    *,
    allow_deep: bool = False,
) -> tuple[list["AlgorithmSpec"], list[dict[str, str]]]:
    """MI-08: drop specs with ``min_rows > n``; DL greyed below 1k unless forced."""
    eligible: list["AlgorithmSpec"] = []
    disabled: list[dict[str, str]] = []
    for spec in specs:
        if spec.min_rows > n_rows:
            disabled.append(
                {
                    "key": spec.key,
                    "reason": f"n={n_rows} < min_rows={spec.min_rows}",
                },
            )
            continue
        if _is_deep_spec(spec) and n_rows < DL_MIN_ROWS_DEFAULT and not allow_deep:
            disabled.append(
                {
                    "key": spec.key,
                    "reason": f"n={n_rows} < {DL_MIN_ROWS_DEFAULT} (DL unless forced)",
                },
            )
            continue
        eligible.append(spec)
    return eligible, disabled


def estimate_training_memory_bytes(
    n_rows: int,
    n_cols: int,
    *,
    model_factor: float = 2.0,
) -> int:
    """MI-09: rows × cols × 8 B × model factor (ARCHITECTURE §46.1)."""
    if n_rows < 0 or n_cols < 0:
        raise ValueError("n_rows and n_cols must be non-negative")
    if model_factor <= 0:
        raise ValueError("model_factor must be positive")
    raw = float(n_rows) * float(n_cols) * float(BYTES_PER_CELL) * float(model_factor)
    return int(raw)


def memory_enqueue_decision(
    estimated_bytes: int,
    worker_limit_bytes: int,
) -> dict[str, Any]:
    """Refuse enqueue above 1.2× worker limit; message includes both numbers."""
    if worker_limit_bytes <= 0:
        raise ValueError("worker_limit_bytes must be positive")
    threshold = int(worker_limit_bytes * REFUSAL_OVER_LIMIT_RATIO)
    allowed = estimated_bytes <= worker_limit_bytes
    refused = estimated_bytes > threshold
    return {
        "estimated_bytes": int(estimated_bytes),
        "worker_limit_bytes": int(worker_limit_bytes),
        "refusal_threshold_bytes": threshold,
        "allowed": allowed and not refused,
        "refused": refused,
        "message": (
            f"refuse: estimated {estimated_bytes} B exceeds "
            f"{REFUSAL_OVER_LIMIT_RATIO}× worker limit {worker_limit_bytes} B "
            f"(threshold {threshold} B)"
            if refused
            else (
                f"estimated={estimated_bytes} B within worker limit {worker_limit_bytes} B"
                if allowed
                else (
                    f"estimated {estimated_bytes} B above worker limit {worker_limit_bytes} B "
                    f"but below refusal threshold {threshold} B — subsample or partial refit"
                )
            )
        ),
    }


def assert_repeated_cv_schemes_registered() -> dict[str, str]:
    """Offline check that repeated K-fold schemes exist in the CV registry."""
    need = {"repeated_kfold", "repeated_stratified_kfold", "leave_one_out"}
    missing = need - set(CV_SCHEME_IDS)
    if missing:
        msg = f"CV registry missing schemes for MI-08: {sorted(missing)}"
        raise ValueError(msg)
    return {"cv_schemes": ",".join(sorted(need))}