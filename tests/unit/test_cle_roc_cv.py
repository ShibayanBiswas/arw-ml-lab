"""CLE.P.ROC_CV — binary ROC curves per fold + mean ± 1 std on common FPR grid."""

from __future__ import annotations

import numpy as np
from labcore.eval.classification.plots import plot_roc_cv
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.model_selection import StratifiedKFold


def _oracle_mean_tpr_on_grid(
    fold_pairs: list[tuple[np.ndarray, np.ndarray]],
    fpr_grid: np.ndarray,
) -> np.ndarray:
    rows: list[np.ndarray] = []
    for y_true, scores in fold_pairs:
        fpr, tpr, _ = roc_curve(y_true, scores)
        rows.append(np.interp(fpr_grid, fpr, tpr, left=0.0, right=1.0))
    return np.vstack(rows).mean(axis=0)


def test_roc_cv_matches_sklearn_oracle():
    X, y = make_classification(
        n_samples=220,
        n_features=10,
        n_informative=4,
        random_state=42,
    )
    cv = StratifiedKFold(n_splits=4, shuffle=True, random_state=42)
    clf = LogisticRegression(max_iter=500, random_state=42)
    folds: list[tuple[np.ndarray, np.ndarray]] = []
    for train_idx, test_idx in cv.split(X, y):
        clf.fit(X[train_idx], y[train_idx])
        folds.append((y[test_idx], clf.predict_proba(X[test_idx])[:, 1]))
    art = plot_roc_cv(folds, n_grid=51)
    assert art["id"] == "CLE.P.ROC_CV"
    grid = np.asarray(art["numbers"]["fpr_grid"])
    mean_t = np.asarray(art["numbers"]["tpr_mean"])
    oracle_mean = _oracle_mean_tpr_on_grid(folds, grid)
    np.testing.assert_allclose(mean_t, oracle_mean, rtol=1e-9, atol=1e-9)
    auc_oracle = [float(roc_auc_score(yt, sc)) for yt, sc in folds]
    assert art["numbers"]["auc_per_fold"] == auc_oracle
    assert art["numbers"]["n_folds"] == 4
    assert len(art["plotly"]["data"]) >= 4