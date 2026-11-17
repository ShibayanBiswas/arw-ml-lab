"""CLU.P.ELBOW — inertia elbow with Kneedle knee."""

from __future__ import annotations

from labcore.unsupervised.cluster_plots import kmeans_elbow
from sklearn.datasets import load_iris


def test_kmeans_elbow_iris():
    X = load_iris().data
    out = kmeans_elbow(X, k_min=2, k_max=8, seed=42)
    assert out["id"] == "CLU.P.ELBOW"
    assert out["seed"] == 42
    assert len(out["numbers"]["inertia"]) == 7
    assert all(w > 0 for w in out["numbers"]["inertia"])
    inertias = out["numbers"]["inertia"]
    assert all(inertias[i] >= inertias[i + 1] for i in range(len(inertias) - 1))
    assert out["numbers"]["knee_k"] in {2, 3, 4, 5, 6, 7, 8, None}
    assert out["plotly"]["data"]