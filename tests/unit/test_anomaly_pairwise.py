"""ANO.P.PAIRWISE — pairwise scatter of top score-linked features."""

from __future__ import annotations

import numpy as np
from labcore.unsupervised.anomaly import fit_anomaly
from labcore.unsupervised.anomaly_plots import anomaly_pairwise_feature_scatter
from sklearn.datasets import load_iris


def test_pairwise_selects_top_features():
    rng = np.random.default_rng(42)
    X = rng.standard_normal((40, 5))
    scores = X[:, 0] * 2.0 + rng.standard_normal(40) * 0.1
    flags = (scores > np.quantile(scores, 0.9)).astype(int)
    names = [f"x{i}" for i in range(5)]
    out = anomaly_pairwise_feature_scatter(
        X, scores, flags, feature_names=names, top_k=3
    )
    assert out["id"] == "ANO.P.PAIRWISE"
    assert out["numbers"]["top_k"] == 3
    assert out["numbers"]["feature"][0] == "x0"
    assert len(out["numbers"]["score_correlation"]) == 3
    assert out["numbers"]["n_pairs"] == 3
    assert out["plotly"]["data"]


def test_pairwise_from_isolation_forest():
    X = load_iris().data
    fitted = fit_anomaly(X, algorithm="isolation_forest", contamination=0.1, seed=42)
    out = anomaly_pairwise_feature_scatter(
        X,
        np.asarray(fitted["scores"]),
        np.asarray(fitted["is_outlier"]),
        feature_names=[f"sepal_{i}" for i in range(X.shape[1])],
        top_k=4,
    )
    assert out["numbers"]["top_k"] == 4
    assert out["numbers"]["n_flagged"] == fitted["n_outliers"]
    assert out["numbers"]["n_inlier"] == len(X) - fitted["n_outliers"]
    assert out["numbers"]["score_separation_cohens_d"] is not None