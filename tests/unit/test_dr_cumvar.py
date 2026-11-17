"""DR.P.CUMVAR — PCA cumulative explained variance."""

from __future__ import annotations

from labcore.unsupervised.dr_plots import pca_cumulative_variance
from sklearn.datasets import load_iris
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


def test_pca_cumulative_variance_iris_matches_sklearn():
    X = load_iris().data
    out = pca_cumulative_variance(X, seed=42)
    assert out["id"] == "DR.P.CUMVAR"
    Xs = StandardScaler().fit_transform(X)
    ref = PCA(n_components=min(X.shape[1], X.shape[0] - 1), random_state=42).fit(Xs)
    cum = (ref.explained_variance_ratio_.cumsum() * 100.0).tolist()
    assert out["numbers"]["cumulative_variance_pct"] == [float(v) for v in cum]
    assert out["numbers"]["k_at_80pct"] is not None
    assert out["numbers"]["k_at_80pct"] <= len(cum)