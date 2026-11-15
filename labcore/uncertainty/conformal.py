"""MAPIE split conformal — regression intervals + APS classification sets."""

from __future__ import annotations

from typing import Any

import numpy as np
from mapie.classification import SplitConformalClassifier
from mapie.regression import SplitConformalRegressor
from mapie.utils import train_conformalize_test_split
from sklearn.base import clone
from sklearn.model_selection import train_test_split


def split_conformal_regression(
    estimator: Any,
    X: np.ndarray,
    y: np.ndarray,
    *,
    confidence_level: float = 0.9,
    seed: int = 42,
) -> dict[str, Any]:
    """
    Split conformal regression via MAPIE SplitConformalRegressor.
    Returns empirical coverage on the held-out test slice.
    """
    # Larger conformalize share → stabler quantile (helps hit 88–92% at 90%)
    X_train, X_conf, X_test, y_train, y_conf, y_test = train_conformalize_test_split(
        X,
        y,
        train_size=0.45,
        conformalize_size=0.35,
        test_size=0.20,
        random_state=seed,
    )
    est = clone(estimator)
    mapie = SplitConformalRegressor(
        estimator=est,
        confidence_level=confidence_level,
        conformity_score="absolute",
        prefit=False,
    )
    mapie.fit(X_train, y_train)
    mapie.conformalize(X_conf, y_conf)
    y_pred, y_pis = mapie.predict_interval(X_test)
    lower = np.asarray(y_pis)[:, 0, 0]
    upper = np.asarray(y_pis)[:, 1, 0]
    y_test_arr = np.asarray(y_test).ravel()
    covered = (y_test_arr >= lower) & (y_test_arr <= upper)
    coverage = float(np.mean(covered))
    return {
        "id": "UQ.T.CONFORMAL_REG",
        "confidence_level": confidence_level,
        "coverage": coverage,
        "n_test": int(len(y_test_arr)),
        "mean_width": float(np.mean(upper - lower)),
        "y_pred": np.asarray(y_pred).ravel().tolist(),
    }


def split_conformal_aps(
    estimator: Any,
    X: np.ndarray,
    y: np.ndarray,
    *,
    confidence_level: float = 0.9,
    seed: int = 42,
) -> dict[str, Any]:
    """APS prediction sets via MAPIE SplitConformalClassifier(conformity_score='aps')."""
    X_tr, X_tmp, y_tr, y_tmp = train_test_split(X, y, test_size=0.5, random_state=seed, stratify=y)
    X_conf, X_te, y_conf, y_te = train_test_split(
        X_tmp, y_tmp, test_size=0.5, random_state=seed, stratify=y_tmp
    )
    est = clone(estimator)
    mapie = SplitConformalClassifier(
        estimator=est,
        confidence_level=confidence_level,
        conformity_score="aps",
        prefit=False,
        random_state=seed,
    )
    mapie.fit(X_tr, y_tr)
    mapie.conformalize(X_conf, y_conf)
    _y_pred, y_ps = mapie.predict_set(X_te, conformity_score_params={"include_last_label": True})
    sets = np.asarray(y_ps)
    y_te_arr = np.asarray(y_te).ravel()
    # MAPIE 1.6 stores the fitted estimator as ``_estimator``
    leaf = getattr(mapie, "estimator_", None) or getattr(mapie, "_estimator", None)
    classes = list(getattr(leaf, "classes_", np.unique(y)))
    covered = []
    for i, yt in enumerate(y_te_arr):
        idx = list(classes).index(yt) if yt in list(classes) else int(yt)
        covered.append(bool(sets[i, idx]))
    coverage = float(np.mean(covered))
    set_sizes = sets.sum(axis=1).astype(float)
    return {
        "id": "UQ.T.CONFORMAL_APS",
        "confidence_level": confidence_level,
        "coverage": coverage,
        "mean_set_size": float(np.mean(set_sizes)),
        "n_test": int(len(y_te_arr)),
    }
