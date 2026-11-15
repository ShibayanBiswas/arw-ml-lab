"""Threshold optimisation on training OOF only (ARCHITECTURE §41.6 subset)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np
from sklearn.metrics import f1_score, roc_curve


def tune_threshold_oof(
    y_oof: np.ndarray,
    proba_oof: np.ndarray,
    *,
    methods: list[str] | None = None,
    cost_fp: float = 1.0,
    cost_fn: float = 1.0,
    spy_test_touched: Callable[[], None] | None = None,
) -> dict[str, Any]:
    """Fit thresholds using OOF only. Never call spy_test_touched from here."""
    _ = spy_test_touched  # reserved for callers; this function must not touch test
    scores = proba_oof[:, 1] if proba_oof.ndim == 2 else proba_oof
    methods = methods or ["youden", "f1", "cost"]
    out: dict[str, Any] = {
        "id": "CLE.T.THRESHOLD_CHOICE",
        "prediction_source": "oof",
        "methods": {},
    }

    fpr, tpr, thr = roc_curve(y_oof, scores)
    # sklearn thr length = len(fpr)-1 sometimes; align
    if len(thr) < len(tpr):
        # pad
        pass
    j = tpr - fpr
    # thr from roc_curve has length len(fpr)-1 when drop_intermediate
    if len(thr) == len(j) - 1:
        j_use = j[1:]
        thr_use = thr
    else:
        j_use = j[: len(thr)]
        thr_use = thr[: len(j_use)]
    if "youden" in methods and len(thr_use):
        i = int(np.nanargmax(j_use))
        out["methods"]["youden"] = {"t_star": float(thr_use[i]), "J": float(j_use[i])}

    if "f1" in methods:
        grid = np.linspace(0.01, 0.99, 99)
        best_t, best_f1 = 0.5, -1.0
        for t in grid:
            pred = (scores >= t).astype(int)
            f1 = f1_score(y_oof, pred, zero_division=0)
            if f1 > best_f1:
                best_f1, best_t = float(f1), float(t)
        out["methods"]["f1"] = {"t_star": best_t, "f1": best_f1}

    if "cost" in methods:
        grid = np.linspace(0.01, 0.99, 99)
        best_t, best_cost = 0.5, float("inf")
        for t in grid:
            pred = (scores >= t).astype(int)
            fp = int(np.sum((pred == 1) & (y_oof == 0)))
            fn = int(np.sum((pred == 0) & (y_oof == 1)))
            c = cost_fp * fp + cost_fn * fn
            if c < best_cost:
                best_cost, best_t = float(c), float(t)
        out["methods"]["cost"] = {"t_star": best_t, "expected_cost": best_cost}

    # default chosen = youden if present else f1
    chosen = out["methods"].get("youden") or out["methods"].get("f1")
    out["chosen"] = chosen
    return out
