"""ANO.P.RANKED — top-N anomaly score bar chart."""

from __future__ import annotations

import numpy as np
from labcore.unsupervised.anomaly import fit_anomaly
from labcore.unsupervised.anomaly_plots import anomaly_ranked_bar
from sklearn.datasets import load_iris


def test_anomaly_ranked_bar_ordering():
    scores = np.array([0.1, 0.9, 0.5, 0.3], dtype=float)
    out = anomaly_ranked_bar(scores, top_n=3)
    assert out["id"] == "ANO.P.RANKED"
    assert out["numbers"]["score"] == sorted(scores.tolist(), reverse=True)[:3]
    assert out["numbers"]["row_index"][0] == 1


def test_ranked_from_isolation_forest():
    X = load_iris().data
    fitted = fit_anomaly(X, algorithm="isolation_forest", contamination=0.1, seed=42)
    ranked = anomaly_ranked_bar(np.asarray(fitted["scores"]), top_n=5)
    assert ranked["numbers"]["top_n"] == 5
    assert ranked["numbers"]["score"] == sorted(fitted["scores"], reverse=True)[:5]