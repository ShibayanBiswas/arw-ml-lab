"""CLE.P.ERROR_OVERLAP — misclassification UpSet across models."""

from __future__ import annotations

import numpy as np
from labcore.eval.classification.plots import plot_error_overlap
from upsetplot import from_contents


def test_error_overlap_oracle_matches_upsetplot():
    rng = np.random.default_rng(42)
    n = 96
    y = rng.integers(0, 2, size=n)
    pred_a = y.copy()
    pred_b = y.copy()
    noise_a = rng.choice(n, size=14, replace=False)
    noise_b = rng.choice(n, size=16, replace=False)
    overlap = noise_a[:6]
    pred_a[noise_a] = 1 - pred_a[noise_a]
    pred_b[noise_b] = 1 - pred_b[noise_b]
    # force 6 rows wrong on both models
    pred_b[overlap] = pred_a[overlap]

    art = plot_error_overlap(y, {"logreg": pred_a, "rf": pred_b})
    assert art["id"] == "CLE.P.ERROR_OVERLAP"
    assert art["numbers"]["status"] == "ok"
    assert art["plotly"]["data"]

    contents = {
        "logreg": {int(i) for i in np.flatnonzero(pred_a != y)},
        "rf": {int(i) for i in np.flatnonzero(pred_b != y)},
    }
    df = from_contents(contents)
    oracle = df.groupby(level=["logreg", "rf"], observed=True).size()
    got = {
        tuple(item["membership"][k] for k in ("logreg", "rf")): item["count"]
        for item in art["numbers"]["intersections"]
    }
    for idx, cnt in oracle.items():
        assert got[idx] == int(cnt)
    assert sum(item["count"] for item in art["numbers"]["intersections"]) == len(
        {int(i) for i in np.flatnonzero((pred_a != y) | (pred_b != y))}
    )