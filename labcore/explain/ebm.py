"""Explainable Boosting Machine via interpret (ARCHITECTURE §17 / R37, C25)."""

from __future__ import annotations

from typing import Any, Literal

import numpy as np
import pandas as pd


def fit_ebm_classifier(
    X: pd.DataFrame | np.ndarray,
    y: np.ndarray | pd.Series,
    *,
    seed: int = 42,
    max_rounds: int = 100,
) -> dict[str, Any]:
    """Fit ``ExplainableBoostingClassifier`` and return global term scores."""
    from interpret.glassbox import ExplainableBoostingClassifier
    from sklearn.metrics import accuracy_score, roc_auc_score
    from sklearn.model_selection import train_test_split

    feature_names = (
        list(X.columns)
        if isinstance(X, pd.DataFrame)
        else [f"f{i}" for i in range(np.asarray(X).shape[1])]
    )
    X_arr = np.asarray(X, dtype=float)
    y_arr = np.asarray(y).ravel()
    X_tr, X_te, y_tr, y_te = train_test_split(
        X_arr, y_arr, test_size=0.25, random_state=seed, stratify=y_arr
    )
    model = ExplainableBoostingClassifier(random_state=seed, max_rounds=max_rounds)
    model.fit(X_tr, y_tr)
    pred = model.predict(X_te)
    proba = model.predict_proba(X_te)[:, 1]
    global_exp = model.explain_global()
    data = global_exp.data()
    names = list(data.get("names", feature_names))
    scores = [float(s) for s in data.get("scores", [])]
    order = np.argsort(scores)[::-1]
    return {
        "id": "EXPLAIN.T.EBM",
        "task": "binary",
        "feature_names": feature_names,
        "term_names": names,
        "term_scores": scores,
        "ranking": [names[i] for i in order],
        "test_accuracy": float(accuracy_score(y_te, pred)),
        "test_roc_auc": float(roc_auc_score(y_te, proba)),
        "seed": seed,
        "max_rounds": max_rounds,
        "library": "interpret",
    }


def fit_ebm(
    X: pd.DataFrame | np.ndarray,
    y: np.ndarray | pd.Series,
    *,
    task: Literal["binary", "regression"] = "binary",
    seed: int = 42,
    max_rounds: int = 100,
) -> dict[str, Any]:
    if task == "binary":
        return fit_ebm_classifier(X, y, seed=seed, max_rounds=max_rounds)
    from interpret.glassbox import ExplainableBoostingRegressor
    from sklearn.metrics import mean_absolute_error, r2_score
    from sklearn.model_selection import train_test_split

    feature_names = (
        list(X.columns)
        if isinstance(X, pd.DataFrame)
        else [f"f{i}" for i in range(np.asarray(X).shape[1])]
    )
    X_arr = np.asarray(X, dtype=float)
    y_arr = np.asarray(y, dtype=float).ravel()
    X_tr, X_te, y_tr, y_te = train_test_split(X_arr, y_arr, test_size=0.25, random_state=seed)
    model = ExplainableBoostingRegressor(random_state=seed, max_rounds=max_rounds)
    model.fit(X_tr, y_tr)
    pred = model.predict(X_te)
    global_exp = model.explain_global()
    data = global_exp.data()
    names = list(data.get("names", feature_names))
    scores = [float(s) for s in data.get("scores", [])]
    return {
        "id": "EXPLAIN.T.EBM",
        "task": "regression",
        "feature_names": feature_names,
        "term_names": names,
        "term_scores": scores,
        "test_r2": float(r2_score(y_te, pred)),
        "test_mae": float(mean_absolute_error(y_te, pred)),
        "seed": seed,
        "max_rounds": max_rounds,
        "library": "interpret",
    }
