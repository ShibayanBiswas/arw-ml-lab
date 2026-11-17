"""DR.P.SCREE — PCA scree + Kaiser rule."""

from __future__ import annotations

from labcore.unsupervised.dr_plots import pca_scree
from sklearn.datasets import load_iris
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


def test_pca_scree_iris_matches_sklearn():
    X = load_iris().data
    out = pca_scree(X, seed=42)
    assert out["id"] == "DR.P.SCREE"
    Xs = StandardScaler().fit_transform(X)
    ref = PCA(n_components=min(X.shape[1], X.shape[0] - 1), random_state=42).fit(Xs)
    assert out["numbers"]["eigenvalue"] == [float(v) for v in ref.explained_variance_]
    assert out["numbers"]["kaiser_k"] == int((ref.explained_variance_ > 1.0).sum())
    assert out["numbers"]["k_at_80pct"] is not None