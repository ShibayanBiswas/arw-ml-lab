"""DR.P.CORR_CIRCLE — PCA correlation circle."""

from __future__ import annotations

import numpy as np
import pytest
from labcore.unsupervised.dr_plots import pca_correlation_circle
from sklearn.datasets import load_iris
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


def test_pca_correlation_circle_iris_matches_sample_correlations():
    X = load_iris().data
    names = [f"x{i}" for i in range(X.shape[1])]
    out = pca_correlation_circle(X, feature_names=names, seed=42)
    assert out["id"] == "DR.P.CORR_CIRCLE"
    Xs = StandardScaler().fit_transform(X)
    ref = PCA(n_components=min(X.shape[1], X.shape[0] - 1), random_state=42).fit(Xs)
    scores = ref.transform(Xs)
    expected_x = np.array(
        [float(np.corrcoef(Xs[:, j], scores[:, 0])[0, 1]) for j in range(X.shape[1])]
    )
    expected_y = np.array(
        [float(np.corrcoef(Xs[:, j], scores[:, 1])[0, 1]) for j in range(X.shape[1])]
    )
    got_x = np.asarray(out["numbers"]["correlation_pc_x"], dtype=float)
    got_y = np.asarray(out["numbers"]["correlation_pc_y"], dtype=float)
    np.testing.assert_allclose(got_x, expected_x, rtol=1e-9, atol=1e-9)
    np.testing.assert_allclose(got_y, expected_y, rtol=1e-9, atol=1e-9)
    assert out["numbers"]["max_radius"] <= 1.0 + 1e-9
    assert out["numbers"]["strong_loading_indices"]
    assert out["numbers"]["explained_variance_ratio_pc_x"] == pytest.approx(
        float(ref.explained_variance_ratio_[0])
    )


def test_pca_correlation_circle_custom_axes():
    X = load_iris().data
    out = pca_correlation_circle(X, pc_x=2, pc_y=3, seed=42)
    assert out["numbers"]["pc_x"] == 2
    assert out["numbers"]["pc_y"] == 3
    assert len(out["numbers"]["correlation_pc_x"]) == X.shape[1]


def test_pca_correlation_circle_rejects_same_axis():
    X = load_iris().data
    with pytest.raises(ValueError, match="must differ"):
        pca_correlation_circle(X, pc_x=1, pc_y=1, seed=42)