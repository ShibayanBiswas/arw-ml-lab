"""Orchestrate regression Eval Core artefacts."""

from __future__ import annotations

from typing import Any

import numpy as np

from labcore.eval.regression.diagnostics import influence_table, residual_table, residual_tests
from labcore.eval.regression.metrics import compute_ree_metrics
from labcore.eval.regression.plots import (
    plot_abs_resid_vs_fitted,
    plot_bland_altman,
    plot_cooks_distance,
    plot_error_hist,
    plot_pred_vs_actual,
    plot_qq,
    plot_residual_acf,
    plot_residual_hist,
    plot_residual_scatter,
    plot_studentised_residuals,
)


def run_regression_eval(
    *,
    y_oof: np.ndarray,
    y_pred_oof: np.ndarray,
    y_test: np.ndarray | None = None,
    y_pred_test: np.ndarray | None = None,
    fold_preds: list[dict[str, np.ndarray]] | None = None,
) -> dict[str, Any]:
    y_oof = np.asarray(y_oof, dtype=float)
    y_pred_oof = np.asarray(y_pred_oof, dtype=float)
    resid = y_oof - y_pred_oof
    metrics = compute_ree_metrics(y_oof, y_pred_oof)
    test_m = None
    if y_test is not None and y_pred_test is not None:
        test_m = compute_ree_metrics(
            np.asarray(y_test, dtype=float), np.asarray(y_pred_test, dtype=float)
        )

    fold_metrics = []
    if fold_preds:
        for fp in fold_preds:
            fold_metrics.append(compute_ree_metrics(fp["y_true"], fp["y_pred"]))

    cv = None
    if fold_metrics:
        keys = fold_metrics[0]
        cv = {
            k: {
                "mean": float(np.nanmean([m[k] for m in fold_metrics])),
                "std": float(np.nanstd([m[k] for m in fold_metrics], ddof=1)),
                "per_fold": [m[k] for m in fold_metrics],
            }
            for k in keys
        }

    infl = influence_table(y_oof, y_pred_oof)
    cooks = np.asarray([r["cooks_d"] for r in infl["rows"]], dtype=float)
    stud = np.asarray([r["studentised_resid"] for r in infl["rows"]], dtype=float)
    plots = [
        plot_pred_vs_actual(y_oof, y_pred_oof),
        plot_residual_scatter(y_pred_oof, resid),
        plot_residual_hist(resid),
        plot_qq(resid),
        plot_cooks_distance(cooks),
        plot_studentised_residuals(stud),
        plot_bland_altman(y_oof, y_pred_oof),
        plot_residual_acf(resid),
        plot_abs_resid_vs_fitted(y_pred_oof, resid),
        plot_error_hist(y_oof, y_pred_oof),
    ]
    return {
        "suite": "regression",
        "residuals": residual_table(y_oof, y_pred_oof),
        "resid_tests": residual_tests(y_oof, y_pred_oof),
        "influence": infl,
        "metrics": metrics,
        "cv_metrics": {"id": "REE.T.CV_METRICS", "metrics": cv} if cv else None,
        "test_metrics": test_m,
        "plots": plots,
        "prediction_source": {"oof": True, "test": y_test is not None},
    }
