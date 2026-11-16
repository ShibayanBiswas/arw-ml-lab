"""DR catalogue plots — Shepard diagram (§36 / 6B)."""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy.spatial.distance import pdist
from scipy.stats import spearmanr


def shepard_diagram(
    X: np.ndarray,
    embedding: np.ndarray,
    *,
    max_pairs: int = 2000,
    seed: int = 42,
) -> dict[str, Any]:
    """DR.P.SHEPARD — high-D vs low-D pairwise distances + Spearman ρ."""
    import plotly.graph_objects as go

    X = np.asarray(X, dtype=float)
    emb = np.asarray(embedding, dtype=float)
    d_hi = pdist(X, metric="euclidean")
    d_lo = pdist(emb, metric="euclidean")
    rho, pval = spearmanr(d_hi, d_lo)
    rng = np.random.default_rng(seed)
    n = len(d_hi)
    if n > max_pairs:
        idx = rng.choice(n, size=max_pairs, replace=False)
        x_plot, y_plot = d_hi[idx], d_lo[idx]
    else:
        x_plot, y_plot = d_hi, d_lo
    fig = go.Figure(go.Scatter(x=x_plot, y=y_plot, mode="markers", opacity=0.35, name="pairs"))
    fig.update_layout(
        title=f"Shepard (Spearman ρ={float(rho):.3f})",
        xaxis_title="High-D distance",
        yaxis_title="Embedding distance",
        height=400,
    )
    return {
        "id": "DR.P.SHEPARD",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {
            "spearman_rho": float(rho) if np.isfinite(rho) else None,
            "pvalue": float(pval) if np.isfinite(pval) else None,
            "n_pairs": int(n),
        },
        "seed": seed,
    }
