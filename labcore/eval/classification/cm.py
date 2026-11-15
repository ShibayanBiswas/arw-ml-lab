"""CLE.T.CM* confusion-matrix suite — sklearn only (ARCHITECTURE §41.2)."""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.metrics import confusion_matrix, multilabel_confusion_matrix


def _nan_safe_div(num: float, den: float) -> float:
    if den == 0:
        return float("nan")
    return float(num / den)


def confusion_suite(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    *,
    labels: list[Any] | None = None,
    fold_matrices: list[np.ndarray] | None = None,
) -> dict[str, Any]:
    """Counts + three normalisations + derived TP/FP/TN/FN + optional fold agg."""
    labels_arr = (
        np.asarray(labels) if labels is not None else np.unique(np.concatenate([y_true, y_pred]))
    )
    cm = confusion_matrix(y_true, y_pred, labels=labels_arr)
    cm_true = confusion_matrix(y_true, y_pred, labels=labels_arr, normalize="true")
    cm_pred = confusion_matrix(y_true, y_pred, labels=labels_arr, normalize="pred")
    cm_all = confusion_matrix(y_true, y_pred, labels=labels_arr, normalize="all")

    mcm = multilabel_confusion_matrix(y_true, y_pred, labels=labels_arr)
    derived: list[dict[str, Any]] = []
    for i, lab in enumerate(labels_arr):
        tn, fp, fn, tp = mcm[i].ravel()
        p = tp + fn
        n = tn + fp
        derived.append(
            {
                "class": _lab_str(lab),
                "support": int(p),
                "actual_negatives": int(n),
                "predicted_positives": int(tp + fp),
                "TP": int(tp),
                "FP": int(fp),
                "FN": int(fn),
                "TN": int(tn),
                "TPR": _nan_safe_div(tp, p),
                "TNR": _nan_safe_div(tn, n),
                "PPV": _nan_safe_div(tp, tp + fp),
                "NPV": _nan_safe_div(tn, tn + fn),
                "FPR": _nan_safe_div(fp, n),
                "FNR": _nan_safe_div(fn, p),
            }
        )

    folds_out: list[dict[str, Any]] = []
    cv_mean_norm: np.ndarray | None = None
    cv_std_norm: np.ndarray | None = None
    if fold_matrices:
        norms = []
        for fi, fm in enumerate(fold_matrices):
            folds_out.append({"fold": fi, "counts": fm.tolist()})
            row_sum = fm.sum(axis=1, keepdims=True)
            with np.errstate(invalid="ignore", divide="ignore"):
                rn = np.divide(
                    fm, row_sum, out=np.full_like(fm, np.nan, dtype=float), where=row_sum != 0
                )
            norms.append(rn)
        stack = np.stack(norms, axis=0)
        cv_mean_norm = np.nanmean(stack, axis=0)
        cv_std_norm = (
            np.nanstd(stack, axis=0, ddof=1) if len(norms) > 1 else np.zeros_like(cv_mean_norm)
        )
        pooled = np.sum(fold_matrices, axis=0)
        # Integrity: pooled counts should match OOF cm when folds partition OOF
        assert pooled.shape == cm.shape

    return {
        "id": "CLE.T.CM",
        "labels": [_lab_str(x) for x in labels_arr],
        "counts": cm.tolist(),
        "norm_true": _tolist_nan(cm_true),
        "norm_pred": _tolist_nan(cm_pred),
        "norm_all": _tolist_nan(cm_all),
        "derived": derived,
        "folds": folds_out,
        "cv_norm_mean": _tolist_nan(cv_mean_norm) if cv_mean_norm is not None else None,
        "cv_norm_std": _tolist_nan(cv_std_norm) if cv_std_norm is not None else None,
        "prediction_source": "oof",
    }


def _lab_str(x: Any) -> str:
    return str(x)


def _tolist_nan(arr: np.ndarray | None) -> list[list[float | None]] | None:
    if arr is None:
        return None
    out: list[list[float | None]] = []
    for row in arr:
        out.append([None if (isinstance(v, float) and np.isnan(v)) else float(v) for v in row])
    return out
