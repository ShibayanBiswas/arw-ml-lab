"""CLE.P.PR_CV — binary PR curves per fold + mean ± 1 std on common recall grid."""

from __future__ import annotations

import numpy as np
from labcore.eval.classification.plots import plot_pr_cv
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, precision_recall_curve
from sklearn.model_selection import StratifiedKFold


def _oracle_mean_precision_on_grid(
    fold_pairs: list[tuple[np.ndarray, np.ndarray]],
    recall_grid: np.ndarray,
) -> np.ndarray:
    rows: list[np.ndarray] = []
    for y_true, scores in fold_pairs:
        p, r, _ = precision_recall_curve(y_true, scores)
        r_inc = np.flip(r)
        p_inc = np.flip(p)
        rows.append(np.interp(recall_grid, r_inc, p_inc, left=1.0, right=0.0))
    return np.vstack(rows).mean(axis=0)


def test_pr_cv_matches_sklearn_oracle():
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
    art = plot_pr_cv(folds, n_grid=51)
    assert art["id"] == "CLE.P.PR_CV"
    grid = np.asarray(art["numbers"]["recall_grid"])
    mean_p = np.asarray(art["numbers"]["precision_mean"])
    oracle_mean = _oracle_mean_precision_on_grid(folds, grid)
    np.testing.assert_allclose(mean_p, oracle_mean, rtol=1e-9, atol=1e-9)
    ap_oracle = [float(average_precision_score(yt, sc)) for yt, sc in folds]
    assert art["numbers"]["ap_per_fold"] == ap_oracle
    assert art["numbers"]["n_folds"] == 4
    assert art["plotly"]["data"]