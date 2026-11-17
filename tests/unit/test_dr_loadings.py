"""DR.P.LOADINGS — PCA loadings heatmap."""

from __future__ import annotations

import numpy as np
import pytest
from labcore.unsupervised.dr_plots import pca_loadings_heatmap
from sklearn.datasets import load_iris
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


def test_pca_loadings_iris_matches_sklearn():
    X = load_iris().data
    names = [f"x{i}" for i in range(X.shape[1])]
    out = pca_loadings_heatmap(X, feature_names=names, seed=42)
    assert out["id"] == "DR.P.LOADINGS"
    Xs = StandardScaler().fit_transform(X)
    ref = PCA(n_components=min(X.shape[1], X.shape[0] - 1), random_state=42).fit(Xs)
    ev = ref.explained_variance_
    expected = (ref.components_.T * np.sqrt(ev)).astype(float)
    got = np.asarray(out["numbers"]["loadings"], dtype=float)
    np.testing.assert_allclose(got, expected, rtol=1e-9, atol=1e-9)
    assert out["numbers"]["n_strong_cells"] >= 1
    assert len(out["numbers"]["strong_cells"]) == out["numbers"]["n_strong_cells"]


def test_pca_loadings_max_components():
    X = load_iris().data
    out = pca_loadings_heatmap(X, seed=42, max_components=2)
    assert len(out["numbers"]["component"]) == 2
    assert np.asarray(out["numbers"]["loadings"]).shape == (X.shape[1], 2)


def test_pca_loadings_rejects_name_mismatch():
    X = load_iris().data
    with pytest.raises(ValueError, match="feature_names"):
        pca_loadings_heatmap(X, feature_names=["a"], seed=42)