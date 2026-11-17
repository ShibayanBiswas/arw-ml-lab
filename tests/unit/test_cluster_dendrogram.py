"""CLU.P.DENDROGRAM — hierarchical dendrogram + cophenetic correlation."""

from __future__ import annotations

from labcore.unsupervised.cluster_plots import hierarchical_dendrogram
from scipy.cluster import hierarchy
from scipy.spatial.distance import pdist
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler


def test_hierarchical_dendrogram_iris():
    X = load_iris().data
    out = hierarchical_dendrogram(X, truncate_p=30, seed=42)
    assert out["id"] == "CLU.P.DENDROGRAM"
    assert out["seed"] == 42
    assert out["numbers"]["n_rows"] == 150
    assert out["numbers"]["linkage_method"] == "ward"
    coph = out["numbers"]["cophenetic_correlation"]
    assert 0.0 < coph <= 1.0

    Xs = StandardScaler().fit_transform(X)
    dist = pdist(Xs, metric="euclidean")
    z_link = hierarchy.linkage(dist, method="ward")
    expected_coph, _ = hierarchy.cophenet(z_link, dist)
    assert coph == expected_coph
    assert out["numbers"]["n_merge_segments"] >= 1
    assert out["plotly"]["data"]