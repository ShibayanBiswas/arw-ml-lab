"""DR.P.BIPLOT — PCA scores + loading arrows."""

from __future__ import annotations

import numpy as np
import pytest
from labcore.unsupervised.dr_plots import pca_biplot
from sklearn.datasets import load_iris
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


def test_pca_biplot_iris_matches_sklearn_loadings():
    X = load_iris().data
    names = [f"x{i}" for i in range(X.shape[1])]
    out = pca_biplot(X, feature_names=names, seed=42)
    assert out["id"] == "DR.P.BIPLOT"
    Xs = StandardScaler().fit_transform(X)
    ref = PCA(n_components=min(X.shape[1], X.shape[0] - 1), random_state=42).fit(Xs)
    ev = ref.explained_variance_
    expected = (ref.components_.T * np.sqrt(ev)).astype(float)
    got = np.asarray(out["numbers"]["loadings"], dtype=float)
    np.testing.assert_allclose(got, expected, rtol=1e-9, atol=1e-9)
    assert out["numbers"]["strong_loading_indices"]
    assert out["numbers"]["explained_variance_ratio_pc_x"] == pytest.approx(
        float(ref.explained_variance_ratio_[0])
    )


def test_pca_biplot_rejects_same_axis():
    X = load_iris().data
    with pytest.raises(ValueError, match="must differ"):
        pca_biplot(X, pc_x=1, pc_y=1, seed=42)