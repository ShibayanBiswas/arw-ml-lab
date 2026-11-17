"""CLE.P.PVALUE_HEATMAP — classification pairwise p-value heatmap."""

from __future__ import annotations

import numpy as np
import pandas as pd
from labcore.eval.classification.plots import plot_pvalue_heatmap
from labcore.eval.regression.plots import _holm_adjust_symmetric
from scikit_posthocs import posthoc_nemenyi_friedman
from statsmodels.stats.multitest import multipletests


def test_cle_pvalue_heatmap_holm_matches_statsmodels():
    rng = np.random.default_rng(42)
    n_folds = 10
    fold_scores = {
        "logreg": rng.uniform(0.82, 0.92, n_folds),
        "rf": rng.uniform(0.78, 0.88, n_folds),
        "gbrt": rng.uniform(0.8, 0.9, n_folds),
    }
    art = plot_pvalue_heatmap(fold_scores, metric="accuracy", higher_is_better=True)
    assert art["id"] == "CLE.P.PVALUE_HEATMAP"
    assert art["numbers"]["status"] == "ok"
    assert art["plotly"]["data"]

    names = list(fold_scores.keys())
    work = pd.DataFrame({k: np.asarray(v, dtype=float) for k, v in fold_scores.items()})
    raw = np.asarray(posthoc_nemenyi_friedman(work.to_numpy()), dtype=float)
    raw_df = pd.DataFrame(raw, index=names, columns=names)
    holm_oracle = _holm_adjust_symmetric(raw_df.to_numpy(dtype=float))

    k = len(names)
    idx_i, idx_j = np.triu_indices(k, k=1)
    pvals = raw_df.to_numpy()[idx_i, idx_j]
    _, padj, _, _ = multipletests(pvals, method="holm")
    for n, (i, j) in enumerate(zip(idx_i, idx_j, strict=True)):
        assert holm_oracle[i, j] == padj[n]

    got = np.array([[art["numbers"]["holm_pvalues"][a][b] for b in names] for a in names])
    np.testing.assert_allclose(got, holm_oracle, rtol=0, atol=1e-9)