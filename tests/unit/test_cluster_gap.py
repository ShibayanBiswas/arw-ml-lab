"""CLU.P.GAP — Tibshirani gap statistic vs k."""

from __future__ import annotations

from labcore.unsupervised.cluster_plots import _kmeans_log_inertia, kmeans_gap_statistic
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler


def test_kmeans_gap_iris():
    X = load_iris().data
    out = kmeans_gap_statistic(X, k_min=2, k_max=6, n_refs=8, seed=42)
    assert out["id"] == "CLU.P.GAP"
    assert out["seed"] == 42
    assert len(out["numbers"]["gap"]) == 5
    assert out["numbers"]["n_refs"] == 8
    assert out["numbers"]["best_k_1se"] in {2, 3, 4, 5, 6}
    assert all(g > 0 for g in out["numbers"]["gap"])
    assert out["plotly"]["data"]

    Xs = StandardScaler().fit_transform(X)
    k = 3
    assert _kmeans_log_inertia(Xs, k, 42) == out["numbers"]["log_wk"][1]