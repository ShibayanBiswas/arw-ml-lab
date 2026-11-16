"""CLU.P.K_SWEEP — silhouette/inertia vs k."""

from __future__ import annotations

from labcore.unsupervised.cluster_plots import kmeans_k_sweep
from sklearn.datasets import load_iris


def test_kmeans_k_sweep_iris():
    X = load_iris().data
    out = kmeans_k_sweep(X, k_min=2, k_max=5, seed=42)
    assert out["id"] == "CLU.P.K_SWEEP"
    assert out["numbers"]["best_k_by_silhouette"] in {2, 3, 4, 5}
    assert len(out["numbers"]["inertia"]) == 4
    assert all(s is not None for s in out["numbers"]["silhouette"])
