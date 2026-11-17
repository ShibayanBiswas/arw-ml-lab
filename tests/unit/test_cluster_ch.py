"""CLU.P.CH — Calinski-Harabasz vs k."""

from __future__ import annotations

from labcore.unsupervised.cluster_plots import kmeans_calinski_harabasz
from sklearn.cluster import KMeans
from sklearn.datasets import load_iris
from sklearn.metrics import calinski_harabasz_score
from sklearn.preprocessing import StandardScaler


def test_kmeans_ch_iris():
    X = load_iris().data
    out = kmeans_calinski_harabasz(X, k_min=2, k_max=8, seed=42)
    assert out["id"] == "CLU.P.CH"
    assert out["seed"] == 42
    assert len(out["numbers"]["calinski_harabasz"]) == 7
    ch = out["numbers"]["calinski_harabasz"]
    assert all(s is None or s > 0 for s in ch)
    assert out["numbers"]["best_k_by_ch"] in {2, 3, 4, 5, 6, 7, 8}
    best = out["numbers"]["best_k_by_ch"]
    Xs = StandardScaler().fit_transform(X)
    km = KMeans(n_clusters=best, random_state=42, n_init=10).fit(Xs)
    expected = float(calinski_harabasz_score(Xs, km.labels_))
    assert out["numbers"]["best_ch"] == expected
    assert out["plotly"]["data"]