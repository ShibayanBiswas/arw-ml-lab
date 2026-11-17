"""CLU.P.DB — Davies-Bouldin vs k."""

from __future__ import annotations

from labcore.unsupervised.cluster_plots import kmeans_davies_bouldin
from sklearn.cluster import KMeans
from sklearn.datasets import load_iris
from sklearn.metrics import davies_bouldin_score
from sklearn.preprocessing import StandardScaler


def test_kmeans_db_iris():
    X = load_iris().data
    out = kmeans_davies_bouldin(X, k_min=2, k_max=8, seed=42)
    assert out["id"] == "CLU.P.DB"
    assert out["seed"] == 42
    assert len(out["numbers"]["davies_bouldin"]) == 7
    db = out["numbers"]["davies_bouldin"]
    assert all(s is None or s > 0 for s in db)
    assert out["numbers"]["best_k_by_db"] in {2, 3, 4, 5, 6, 7, 8}
    best = out["numbers"]["best_k_by_db"]
    Xs = StandardScaler().fit_transform(X)
    km = KMeans(n_clusters=best, random_state=42, n_init=10).fit(Xs)
    expected = float(davies_bouldin_score(Xs, km.labels_))
    assert out["numbers"]["best_db"] == expected
    assert out["plotly"]["data"]