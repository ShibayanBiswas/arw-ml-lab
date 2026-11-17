"""REE.P.PRED_ACTUAL_FOLDS — per-fold predicted vs actual."""

from __future__ import annotations

import numpy as np
from labcore.eval.regression.plots import plot_pred_actual_folds
from labcore.eval.regression.metrics import compute_ree_metrics


def test_pred_actual_folds_sklearn_metrics_and_shape():
    rng = np.random.default_rng(42)
    fold_preds: list[dict[str, np.ndarray]] = []
    for k in range(3):
        n = 40 + k * 5
        y_true = rng.normal(10 + k, 2, n)
        y_pred = y_true + rng.normal(0, 0.3 + 0.1 * k, n)
        fold_preds.append({"y_true": y_true, "y_pred": y_pred})

    art = plot_pred_actual_folds(fold_preds)
    assert art["id"] == "REE.P.PRED_ACTUAL_FOLDS"
    assert art["numbers"]["n_folds"] == 3
    assert len(art["numbers"]["per_fold"]) == 3
    assert len(art["plotly"]["data"]) >= 6

    for fp, block in zip(fold_preds, art["numbers"]["per_fold"], strict=True):
        yt = np.asarray(fp["y_true"], dtype=float)
        yp = np.asarray(fp["y_pred"], dtype=float)
        met = compute_ree_metrics(yt, yp)
        assert block["r2"] == met["REE.M.01"]
        assert block["rmse"] == met["REE.M.02"]
        np.testing.assert_allclose(block["y_true"], yt, rtol=0, atol=1e-12)
        np.testing.assert_allclose(block["y_pred"], yp, rtol=0, atol=1e-12)