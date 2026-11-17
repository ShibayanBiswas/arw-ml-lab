"""ANO.P.EMBED — PCA scatter with flagged anomalies."""

from __future__ import annotations

import numpy as np
from labcore.unsupervised.anomaly import fit_anomaly
from labcore.unsupervised.anomaly_plots import anomaly_embedding_scatter
from sklearn.datasets import load_iris


def test_anomaly_embedding_scatter_ids():
    X = load_iris().data
    fitted = fit_anomaly(X, algorithm="isolation_forest", contamination=0.1, seed=42)
    out = anomaly_embedding_scatter(
        X,
        np.asarray(fitted["scores"]),
        np.asarray(fitted["is_outlier"]),
        seed=42,
    )
    assert out["id"] == "ANO.P.EMBED"
    assert out["seed"] == 42
    assert out["numbers"]["n_flagged"] == fitted["n_outliers"]
    assert out["numbers"]["n_inlier"] == len(X) - fitted["n_outliers"]
    assert out["numbers"]["explained_variance_ratio_pc1"] is not None


def test_embedding_flags_match():
    scores = np.array([0.1, 0.5, 0.9, 0.2], dtype=float)
    flags = np.array([0, 0, 1, 0], dtype=int)
    X = np.eye(4)
    out = anomaly_embedding_scatter(X, scores, flags, seed=42)
    assert out["numbers"]["n_flagged"] == 1
    assert out["numbers"]["score_separation_cohens_d"] is not None