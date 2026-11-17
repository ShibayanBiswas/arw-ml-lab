"""ANO.P.SCORE_HIST — histogram with threshold and inlier/flagged split."""

from __future__ import annotations

import numpy as np
from labcore.unsupervised.anomaly import fit_anomaly
from labcore.unsupervised.anomaly_plots import anomaly_score_hist
from sklearn.datasets import load_iris


def test_anomaly_score_hist_artefact():
    scores = np.array([0.2, 0.25, 0.3, 0.8, 0.9], dtype=float)
    flags = np.array([0, 0, 0, 1, 1], dtype=int)
    out = anomaly_score_hist(scores, threshold=0.5, is_outlier=flags)
    assert out["id"] == "ANO.P.SCORE_HIST"
    assert out["numbers"]["n_flagged"] == 2
    assert out["numbers"]["n_inlier"] == 3
    assert out["numbers"]["n_above_threshold"] == 2
    assert out["numbers"]["score_separation_cohens_d"] is not None


def test_isolation_forest_includes_score_hist():
    X = load_iris().data
    out = fit_anomaly(X, algorithm="isolation_forest", contamination=0.1, seed=42)
    assert out["n_outliers"] >= 1
    hist = out["plots"][0]
    assert hist["id"] == "ANO.P.SCORE_HIST"
    assert hist["numbers"]["n_flagged"] == out["n_outliers"]
    assert out["threshold"] is not None
    assert hist["numbers"]["threshold"] == out["threshold"]


def test_score_hist_from_isolation_forest_route_payload():
    X = load_iris().data
    fitted = fit_anomaly(X, algorithm="isolation_forest", contamination=0.1, seed=42)
    hist = anomaly_score_hist(
        np.asarray(fitted["scores"]),
        threshold=fitted["threshold"],
        is_outlier=np.asarray(fitted["is_outlier"]),
    )
    assert hist["numbers"]["score_separation_cohens_d"] is not None