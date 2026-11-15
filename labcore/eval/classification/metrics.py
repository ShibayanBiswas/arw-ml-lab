"""CLE.M.* scalar metrics — library wrappers (ARCHITECTURE §41.4). Binary + multiclass."""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    cohen_kappa_score,
    f1_score,
    fbeta_score,
    hamming_loss,
    jaccard_score,
    log_loss,
    matthews_corrcoef,
    precision_score,
    recall_score,
    roc_auc_score,
    top_k_accuracy_score,
)


def compute_cle_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_proba: np.ndarray | None = None,
    *,
    task: str = "binary",
) -> dict[str, float]:
    """Return CLE.M.* values applicable to binary/multiclass; missing → nan."""
    out: dict[str, float] = {}
    # sklearn jaccard only accepts 0/1/'warn' for zero_division; others accept nan
    zd_nan: float = float("nan")
    out["CLE.M.01"] = float(accuracy_score(y_true, y_pred))
    out["CLE.M.02"] = 1.0 - out["CLE.M.01"]
    out["CLE.M.03"] = float(balanced_accuracy_score(y_true, y_pred))
    avg = "binary" if task == "binary" else "macro"
    out["CLE.M.04"] = float(precision_score(y_true, y_pred, average=avg, zero_division=zd_nan))
    out["CLE.M.05"] = float(recall_score(y_true, y_pred, average=avg, zero_division=zd_nan))
    try:
        from imblearn.metrics import geometric_mean_score, specificity_score

        out["CLE.M.06"] = float(
            specificity_score(y_true, y_pred, average=avg, zero_division=zd_nan)
        )
        out["CLE.M.12"] = float(geometric_mean_score(y_true, y_pred, average=avg))
    except Exception:
        out["CLE.M.06"] = float("nan")
        out["CLE.M.12"] = float("nan")
    out["CLE.M.10"] = float(f1_score(y_true, y_pred, average=avg, zero_division=zd_nan))
    out["CLE.M.11"] = float(
        fbeta_score(y_true, y_pred, beta=2.0, average=avg, zero_division=zd_nan)
    )
    out["CLE.M.14"] = float(matthews_corrcoef(y_true, y_pred))
    out["CLE.M.15"] = float(cohen_kappa_score(y_true, y_pred))
    if task != "binary":
        out["CLE.M.17"] = float(cohen_kappa_score(y_true, y_pred, weights="quadratic"))
    out["CLE.M.22"] = float(jaccard_score(y_true, y_pred, average=avg, zero_division=0))
    out["CLE.M.39"] = float(hamming_loss(y_true, y_pred))

    if y_proba is not None:
        try:
            if task == "binary":
                scores = y_proba[:, 1] if y_proba.ndim == 2 else y_proba
                out["CLE.M.24"] = float(log_loss(y_true, y_proba if y_proba.ndim == 2 else scores))
                out["CLE.M.26"] = float(brier_score_loss(y_true, scores))
                out["CLE.M.30"] = float(roc_auc_score(y_true, scores))
                out["CLE.M.34"] = float(average_precision_score(y_true, scores))
                out["CLE.M.37"] = 2.0 * out["CLE.M.30"] - 1.0
                out["CLE.M.46"] = _ece(y_true, scores)
                out["CLE.M.47"] = _mce(y_true, scores)
            else:
                out["CLE.M.24"] = float(log_loss(y_true, y_proba, labels=np.unique(y_true)))
                out["CLE.M.31"] = float(
                    roc_auc_score(y_true, y_proba, multi_class="ovr", average="macro")
                )
                out["CLE.M.34"] = float(
                    average_precision_score(y_true, y_proba, average="macro")
                )
                try:
                    out["CLE.M.38"] = float(top_k_accuracy_score(y_true, y_proba, k=3))
                except Exception:
                    out["CLE.M.38"] = float("nan")
        except Exception:
            pass
    return out


def aggregate_cv_metrics(
    fold_metrics: list[dict[str, float]],
    *,
    pooled: dict[str, float] | None = None,
    test: dict[str, float] | None = None,
    train: dict[str, float] | None = None,
) -> dict[str, Any]:
    """CLE.T.CV_METRICS — mean±std, SEM, min/max, pooled, gaps."""
    if not fold_metrics:
        return {"id": "CLE.T.CV_METRICS", "metrics": {}}
    keys = sorted({k for m in fold_metrics for k in m})
    table: dict[str, Any] = {}
    n = len(fold_metrics)
    for k in keys:
        vals = np.array([m.get(k, np.nan) for m in fold_metrics], dtype=float)
        mean = float(np.nanmean(vals))
        std = float(np.nanstd(vals, ddof=1)) if n > 1 else 0.0
        sem = float(std / np.sqrt(n)) if n else float("nan")
        # 95% CI on fold mean (t approx via normal for thin core)
        ci = 1.96 * sem
        row = {
            "mean": mean,
            "std": std,
            "sem": sem,
            "min": float(np.nanmin(vals)),
            "max": float(np.nanmax(vals)),
            "ci95_low": mean - ci,
            "ci95_high": mean + ci,
            "per_fold": [_nan(v) for v in vals],
        }
        if pooled and k in pooled:
            row["pooled_oof"] = pooled[k]
        if test and k in test:
            row["test"] = test[k]
        if train and k in train and pooled and k in pooled:
            row["train_cv_gap"] = float(train[k] - pooled[k]) if not (
                np.isnan(train[k]) or np.isnan(pooled[k])
            ) else float("nan")
        table[k] = row
    return {"id": "CLE.T.CV_METRICS", "n_folds": n, "metrics": table}


def _ece(y_true: np.ndarray, scores: np.ndarray, n_bins: int = 15) -> float:
    try:
        from netcal.metrics import ECE  # type: ignore[import-untyped]

        return float(ECE(n_bins).measure(scores, y_true))
    except Exception:
        return float("nan")


def _mce(y_true: np.ndarray, scores: np.ndarray, n_bins: int = 15) -> float:
    try:
        from netcal.metrics import MCE  # type: ignore[import-untyped]

        return float(MCE(n_bins).measure(scores, y_true))
    except Exception:
        return float("nan")


def _nan(v: float) -> float | None:
    return None if np.isnan(v) else float(v)
