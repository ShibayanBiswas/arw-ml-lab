"""CLU.P.CLUSTERMAP — clustered feature correlation heatmap."""

from __future__ import annotations

import numpy as np
from labcore.unsupervised.cluster_plots import correlation_clustermap
from scipy.cluster import hierarchy
from scipy.spatial.distance import squareform
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler


def test_correlation_clustermap_iris():
    X = load_iris().data
    names = [f"f{i}" for i in range(4)]
    out = correlation_clustermap(X, feature_names=names, seed=42)
    assert out["id"] == "CLU.P.CLUSTERMAP"
    assert out["seed"] == 42
    assert out["numbers"]["n_features"] == 4
    assert len(out["numbers"]["feature_order"]) == 4
    assert len(out["numbers"]["correlation"]) == 4
    coph = out["numbers"]["cophenetic_correlation"]
    assert 0.0 < coph <= 1.0

    Xs = StandardScaler().fit_transform(X)
    corr = np.corrcoef(Xs.T)
    dist_sq = np.clip(2.0 * (1.0 - corr), 0.0, None)
    z_link = hierarchy.linkage(squareform(dist_sq, checks=False), method="average")
    expected_coph, _ = hierarchy.cophenet(z_link, np.sqrt(squareform(dist_sq, checks=False)))
    assert coph == expected_coph
    assert out["numbers"]["n_dendro_segments"] >= 1
    assert out["plotly"]["data"]