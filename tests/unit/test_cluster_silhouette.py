"""CLU.P.SILHOUETTE — silhouette knife plot."""

from __future__ import annotations

from labcore.unsupervised.cluster_plots import silhouette_knife
from sklearn.datasets import load_iris


def test_silhouette_knife_iris():
    X = load_iris().data
    out = silhouette_knife(X, n_clusters=3, seed=42)
    assert out["id"] == "CLU.P.SILHOUETTE"
    assert out["numbers"]["n_clusters"] == 3
    assert len(out["numbers"]["cluster_mean_silhouette"]) == 3
    assert sum(out["numbers"]["cluster_sizes"].values()) == 150
    assert -1.0 <= out["numbers"]["overall_silhouette"] <= 1.0