"""Critical-difference diagram helpers (Friedman + Nemenyi).

Uses ``scipy.stats.friedmanchisquare`` and ``scikit_posthocs.posthoc_nemenyi_friedman``.
Plotly rendering of mean ranks + CD bar (Demšar 2006).
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scikit_posthocs import posthoc_nemenyi_friedman
from scipy.stats import friedmanchisquare


def friedman_nemenyi(
    scores: pd.DataFrame,
    *,
    alpha: float = 0.05,
) -> dict[str, Any]:
    """``scores``: rows = datasets/folds, columns = models (higher is better)."""
    if scores.shape[1] < 2 or scores.shape[0] < 2:
        return {"status": "not computed", "reason": "need ≥2 models and ≥2 rows"}
    cols = list(scores.columns)
    arrays = [scores[c].to_numpy(dtype=float) for c in cols]
    stat, pval = friedmanchisquare(*arrays)
    # ranks: average rank per model (1 = best)
    ranks = scores.rank(axis=1, ascending=False, method="average")
    mean_ranks = ranks.mean(axis=0).to_dict()
    posthoc = posthoc_nemenyi_friedman(scores.to_numpy())
    posthoc_df = pd.DataFrame(posthoc, index=cols, columns=cols)
    k = len(cols)
    n = len(scores)
    # Critical difference (Demšar): q_alpha * sqrt(k(k+1)/(6n))
    # q_0.05 for common k approximated via studentized range; use 2.569 for k≈3..10 thin
    q_alpha = {
        2: 1.960,
        3: 2.343,
        4: 2.569,
        5: 2.728,
        6: 2.850,
        7: 2.949,
        8: 3.031,
        9: 3.102,
        10: 3.164,
    }.get(k, 3.2)
    cd = float(q_alpha * np.sqrt(k * (k + 1) / (6.0 * n)))
    return {
        "status": "ok",
        "friedman_statistic": float(stat),
        "friedman_pvalue": float(pval),
        "alpha": alpha,
        "significant": bool(pval < alpha),
        "mean_ranks": {str(k_): float(v) for k_, v in mean_ranks.items()},
        "critical_difference": cd,
        "nemenyi_pvalues": posthoc_df.to_dict(),
        "n_models": k,
        "n_rows": n,
        "seed": 42,
    }


def plot_cd_ranks(result: dict[str, Any]) -> dict[str, Any]:
    """Return a Plotly figure dict for mean ranks with CD whisker."""
    if result.get("status") != "ok":
        return {"data": [], "layout": {"title": "CD diagram not computed"}}
    ranks = result["mean_ranks"]
    names = list(ranks.keys())
    vals = [ranks[n] for n in names]
    order = np.argsort(vals)
    names = [names[i] for i in order]
    vals = [vals[i] for i in order]
    cd = float(result["critical_difference"])
    # Best (lowest rank) CD bar
    best = vals[0]
    fig = {
        "data": [
            {
                "type": "scatter",
                "mode": "markers+text",
                "x": vals,
                "y": names,
                "text": [f"{v:.2f}" for v in vals],
                "textposition": "middle right",
                "marker": {"size": 10, "color": "#c9a227"},
                "name": "mean rank",
            },
            {
                "type": "scatter",
                "mode": "lines",
                "x": [best, best + cd],
                "y": [names[0], names[0]],
                "line": {"color": "#333", "width": 3},
                "name": f"CD={cd:.3f}",
            },
        ],
        "layout": {
            "title": "Critical difference (mean ranks)",
            "xaxis": {"title": "Average rank (lower better)", "autorange": "reversed"},
            "yaxis": {"title": ""},
            "showlegend": True,
        },
    }
    return fig
