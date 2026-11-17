"""CLU.P.K_DISTANCE — DBSCAN k-distance / eps knee."""

from __future__ import annotations

from labcore.unsupervised.cluster_plots import dbscan_k_distance
from sklearn.datasets import load_iris


def test_dbscan_k_distance_iris():
    X = load_iris().data
    out = dbscan_k_distance(X, min_samples=5, seed=42)
    assert out["id"] == "CLU.P.K_DISTANCE"
    assert out["seed"] == 42
    nums = out["numbers"]
    assert nums["n_rows"] == len(X)
    assert nums["min_samples"] == 5
    assert len(nums["k_distance_sorted"]) == len(X)
    assert nums["k_distance_sorted"][0] >= nums["k_distance_sorted"][-1]
    assert nums["suggested_eps"] is not None
    assert nums["suggested_eps"] > 0
    assert out["plotly"]["data"]