"""Orchestrate classification Eval Core artefacts."""

from __future__ import annotations

from typing import Any

import numpy as np

from labcore.eval.classification.cm import confusion_suite
from labcore.eval.classification.compare import delong_test, mcnemar_test
from labcore.eval.classification.metrics import aggregate_cv_metrics, compute_cle_metrics
from labcore.eval.classification.plots import plot_confusion, plot_pr, plot_reliability, plot_roc
from labcore.eval.classification.report import classification_report_table
from labcore.eval.classification.threshold import tune_threshold_oof


def run_classification_eval(
    *,
    y_oof: np.ndarray,
    y_pred_oof: np.ndarray,
    y_proba_oof: np.ndarray | None = None,
    y_test: np.ndarray | None = None,
    y_pred_test: np.ndarray | None = None,
    y_proba_test: np.ndarray | None = None,
    fold_preds: list[dict[str, np.ndarray]] | None = None,
    task: str = "binary",
    labels: list[Any] | None = None,
    compare_alt_pred: np.ndarray | None = None,
    compare_alt_scores: np.ndarray | None = None,
    test_touch_spy: list[str] | None = None,
) -> dict[str, Any]:
    """Build §41 core payload. Threshold tuning uses OOF only."""
    y_oof = np.asarray(y_oof)
    y_pred_oof = np.asarray(y_pred_oof)
    labels = labels if labels is not None else sorted(np.unique(y_oof).tolist())

    fold_cms = None
    fold_metrics: list[dict[str, float]] = []
    if fold_preds:
        fold_cms = []
        for fp in fold_preds:
            from sklearn.metrics import confusion_matrix

            fold_cms.append(
                confusion_matrix(fp["y_true"], fp["y_pred"], labels=labels)
            )
            fold_metrics.append(
                compute_cle_metrics(
                    fp["y_true"],
                    fp["y_pred"],
                    fp.get("y_proba"),
                    task=task,
                )
            )

    cm = confusion_suite(y_oof, y_pred_oof, labels=labels, fold_matrices=fold_cms)
    report = classification_report_table(y_oof, y_pred_oof, y_proba_oof, labels=labels)
    pooled_m = compute_cle_metrics(y_oof, y_pred_oof, y_proba_oof, task=task)
    test_m = None
    if y_test is not None and y_pred_test is not None:
        if test_touch_spy is not None:
            test_touch_spy.append("metrics_test")
        test_m = compute_cle_metrics(y_test, y_pred_test, y_proba_test, task=task)

    if not fold_metrics:
        fold_metrics = [pooled_m]
    cv_table = aggregate_cv_metrics(fold_metrics, pooled=pooled_m, test=test_m)

    threshold = None
    if task == "binary" and y_proba_oof is not None:
        # Must not read test for tuning
        threshold = tune_threshold_oof(y_oof, y_proba_oof)

    plots: list[dict[str, Any]] = [
        plot_confusion(
            cm["counts"], cm["labels"], title="Confusion (counts)", plot_id="CLE.P.CM"
        ),
        plot_confusion(
            cm["norm_true"],
            cm["labels"],
            title="Confusion (row/true)",
            plot_id="CLE.P.CM_NORM_TRUE",
        ),
    ]
    if task == "binary" and y_proba_oof is not None:
        scores = y_proba_oof[:, 1] if y_proba_oof.ndim == 2 else y_proba_oof
        plots.extend(
            [
                plot_roc(y_oof, scores),
                plot_pr(y_oof, scores),
                plot_reliability(y_oof, scores),
            ]
        )

    compare: dict[str, Any] = {}
    if compare_alt_pred is not None:
        compare["mcnemar"] = mcnemar_test(y_oof, y_pred_oof, compare_alt_pred)
    if compare_alt_scores is not None and y_proba_oof is not None:
        sa = y_proba_oof[:, 1] if y_proba_oof.ndim == 2 else y_proba_oof
        compare["delong"] = delong_test(y_oof, sa, compare_alt_scores)

    return {
        "suite": "classification",
        "task": task,
        "cm": cm,
        "report": report,
        "metrics": pooled_m,
        "cv_metrics": cv_table,
        "threshold": threshold,
        "test_metrics": test_m,
        "plots": plots,
        "compare": compare,
        "prediction_source": {"oof": True, "test": y_test is not None},
    }
