"""EBM thin wrapper (interpret glassbox)."""

from __future__ import annotations

from labcore.explain.ebm import fit_ebm
from sklearn.datasets import load_breast_cancer


def test_ebm_binary_global_scores():
    X, y = load_breast_cancer(return_X_y=True, as_frame=True)
    out = fit_ebm(X, y, task="binary", seed=42, max_rounds=40)
    assert out["id"] == "EXPLAIN.T.EBM"
    assert out["test_roc_auc"] > 0.9
    assert len(out["term_scores"]) >= 1
    assert len(out["ranking"]) == len(out["term_names"])
