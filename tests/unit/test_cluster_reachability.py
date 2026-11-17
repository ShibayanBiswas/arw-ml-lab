"""CLU.P.REACHABILITY — OPTICS reachability diagram."""

from __future__ import annotations

from labcore.unsupervised.cluster_plots import optics_reachability
from sklearn.datasets import load_iris


def test_optics_reachability_iris():
    X = load_iris().data
    out = optics_reachability(X, min_samples=5, seed=42)
    assert out["id"] == "CLU.P.REACHABILITY"
    assert out["seed"] == 42
    nums = out["numbers"]
    assert nums["n_rows"] == len(X)
    assert nums["min_samples"] == 5
    assert len(nums["ordering"]) == len(X)
    assert len(nums["reachability_ordered"]) == len(X)
    assert nums["n_clusters"] >= 1
    assert all(r >= 0 or r == float("inf") for r in nums["reachability_ordered"])
    assert out["plotly"]["data"]