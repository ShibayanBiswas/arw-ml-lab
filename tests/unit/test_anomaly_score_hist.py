"""ANO.P.SCORE_HIST via IsolationForest."""

from __future__ import annotations

from labcore.unsupervised.anomaly import fit_anomaly
from sklearn.datasets import load_iris


def test_isolation_forest_includes_score_hist():
    X = load_iris().data
    out = fit_anomaly(X, algorithm="isolation_forest", contamination=0.1, seed=42)
    assert out["n_outliers"] >= 1
    assert out["plots"][0]["id"] == "ANO.P.SCORE_HIST"
    assert out["threshold"] is not None
