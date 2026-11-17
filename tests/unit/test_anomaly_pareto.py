"""ANO.P.PARETO — ranked score curve with cumulative mass."""

from __future__ import annotations

import numpy as np
from labcore.unsupervised.anomaly import fit_anomaly
from labcore.unsupervised.anomaly_plots import anomaly_pareto_rank
from sklearn.datasets import load_iris


def test_anomaly_pareto_rank_ordering():
    scores = np.array([0.1, 0.9, 0.5, 0.3], dtype=float)
    out = anomaly_pareto_rank(scores, threshold=0.4)
    assert out["id"] == "ANO.P.PARETO"
    assert out["numbers"]["score"] == sorted(scores.tolist(), reverse=True)
    assert out["numbers"]["n"] == 4
    assert out["numbers"]["cumulative_pct"][-1] == 100.0
    assert out["numbers"]["elbow_rank"] is not None


def test_pareto_from_isolation_forest():
    X = load_iris().data
    fitted = fit_anomaly(X, algorithm="isolation_forest", contamination=0.1, seed=42)
    pareto = anomaly_pareto_rank(
        np.asarray(fitted["scores"]),
        threshold=fitted["threshold"],
    )
    assert pareto["numbers"]["n"] == len(fitted["scores"])
    assert len(pareto["numbers"]["rank"]) == pareto["numbers"]["n"]
    assert pareto["numbers"]["threshold"] == fitted["threshold"]
    assert pareto["plotly"]["data"]