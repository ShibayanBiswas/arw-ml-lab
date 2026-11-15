"""CLE.T.REPORT — library-backed classification report (ARCHITECTURE §41.3)."""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    classification_report,
    fbeta_score,
    multilabel_confusion_matrix,
    precision_recall_fscore_support,
    roc_auc_score,
)


def classification_report_table(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_proba: np.ndarray | None = None,
    *,
    labels: list[Any] | None = None,
) -> dict[str, Any]:
    labels_arr = np.asarray(labels) if labels is not None else np.unique(y_true)
    p, r, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=labels_arr, zero_division=np.nan
    )
    f05 = fbeta_score(
        y_true, y_pred, beta=0.5, labels=labels_arr, average=None, zero_division=np.nan
    )
    f2 = fbeta_score(
        y_true, y_pred, beta=2.0, labels=labels_arr, average=None, zero_division=np.nan
    )
    mcm = multilabel_confusion_matrix(y_true, y_pred, labels=labels_arr)

    rows: list[dict[str, Any]] = []
    for i, lab in enumerate(labels_arr):
        tn, fp, fn, tp = mcm[i].ravel().astype(float)
        row: dict[str, Any] = {
            "class": str(lab),
            "support": int(support[i]),
            "precision": _f(p[i]),
            "recall": _f(r[i]),
            "f1": _f(f1[i]),
            "fbeta_0.5": _f(f05[i]),
            "fbeta_2": _f(f2[i]),
            "specificity": _div(tn, tn + fp),
            "npv": _div(tn, tn + fn),
            "fpr": _div(fp, tn + fp),
            "fnr": _div(fn, tp + fn),
        }
        if y_proba is not None:
            try:
                if y_proba.ndim == 1 or y_proba.shape[1] == 2:
                    scores = y_proba if y_proba.ndim == 1 else y_proba[:, 1]
                    if len(labels_arr) == 2 and i == 1:
                        row["roc_auc_ovr"] = float(
                            roc_auc_score((y_true == lab).astype(int), scores)
                        )
                        row["average_precision_ovr"] = float(
                            average_precision_score((y_true == lab).astype(int), scores)
                        )
                elif y_proba.shape[1] == len(labels_arr):
                    row["roc_auc_ovr"] = float(
                        roc_auc_score((y_true == lab).astype(int), y_proba[:, i])
                    )
                    row["average_precision_ovr"] = float(
                        average_precision_score((y_true == lab).astype(int), y_proba[:, i])
                    )
            except Exception:
                row["roc_auc_ovr"] = float("nan")
        rows.append(row)

    sk_dict = classification_report(
        y_true, y_pred, labels=labels_arr, output_dict=True, zero_division=np.nan
    )
    footer = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "macro_avg": _avg_row(sk_dict.get("macro avg")),
        "weighted_avg": _avg_row(sk_dict.get("weighted avg")),
        "micro_avg": _avg_row(sk_dict.get("micro avg")) if "micro avg" in sk_dict else None,
    }
    return {
        "id": "CLE.T.REPORT",
        "rows": rows,
        "footer": footer,
        "sklearn_report": sk_dict,
        "prediction_source": "oof",
    }


def _f(v: Any) -> float:
    return (
        float(v) if v is not None and not (isinstance(v, float) and np.isnan(v)) else float("nan")
    )


def _div(a: float, b: float) -> float:
    return float(a / b) if b else float("nan")


def _avg_row(d: dict[str, Any] | None) -> dict[str, float] | None:
    if not d:
        return None
    return {
        "precision": float(d.get("precision", float("nan"))),
        "recall": float(d.get("recall", float("nan"))),
        "f1": float(d.get("f1-score", float("nan"))),
        "support": float(d.get("support", float("nan"))),
    }
