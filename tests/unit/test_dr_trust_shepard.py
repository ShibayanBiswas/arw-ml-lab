"""DR trustworthiness + Shepard diagram (6B thin)."""

from __future__ import annotations

from labcore.unsupervised.dr import fit_dr
from labcore.unsupervised.dr_plots import shepard_diagram
from sklearn.datasets import load_iris


def test_pca_trustworthiness_and_shepard():
    X = load_iris().data
    out = fit_dr(X, algorithm="pca", n_components=2, seed=42)
    assert out["trustworthiness"] is not None
    assert 0.0 <= float(out["trustworthiness"]) <= 1.0
    shepard = shepard_diagram(X, out["embedding"], seed=42)
    assert shepard["id"] == "DR.P.SHEPARD"
    assert shepard["numbers"]["spearman_rho"] is not None
