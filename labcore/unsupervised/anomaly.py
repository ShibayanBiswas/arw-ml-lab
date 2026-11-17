"""Anomaly detection — sklearn / pyod thin wrappers (ARCHITECTURE §18)."""

from __future__ import annotations

from typing import Any, Literal

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler

AnomalyAlgo = Literal["isolation_forest", "lof", "pyod_copod"]


def fit_anomaly(
    X: pd.DataFrame | np.ndarray,
    *,
    algorithm: AnomalyAlgo = "isolation_forest",
    contamination: float = 0.05,
    seed: int = 42,
) -> dict[str, Any]:
    """Fit an anomaly detector; return scores + binary flags (library-computed)."""
    X_arr = np.asarray(X, dtype=float)
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X_arr)

    if algorithm == "isolation_forest":
        model = IsolationForest(
            contamination=contamination,
            random_state=seed,
            n_estimators=100,
        )
        flags = model.fit_predict(Xs)  # 1 inlier, -1 outlier
        scores = -model.score_samples(Xs)  # higher = more anomalous
    elif algorithm == "lof":
        model = LocalOutlierFactor(contamination=contamination, novelty=False)
        flags = model.fit_predict(Xs)
        scores = -model.negative_outlier_factor_
    elif algorithm == "pyod_copod":
        from pyod.models.copod import COPOD  # type: ignore[import-not-found]

        model = COPOD(contamination=contamination)
        model.fit(Xs)
        scores = np.asarray(model.decision_scores_, dtype=float)
        flags = np.where(model.labels_ == 1, -1, 1)
    else:
        raise ValueError(f"unknown anomaly algorithm: {algorithm}")

    is_outlier = (np.asarray(flags) == -1).astype(int)
    scores_arr = np.asarray(scores, dtype=float)
    thr = float(np.quantile(scores_arr, 1.0 - contamination)) if len(scores_arr) else None
    from labcore.unsupervised.anomaly_plots import anomaly_score_hist

    return {
        "id": f"UNSUP.ANOMALY.{algorithm}",
        "algorithm": algorithm,
        "scores": scores_arr.tolist(),
        "is_outlier": is_outlier.tolist(),
        "n_outliers": int(is_outlier.sum()),
        "contamination": float(contamination),
        "threshold": thr,
        "plots": [anomaly_score_hist(scores_arr, threshold=thr, is_outlier=is_outlier)],
        "seed": seed,
    }
