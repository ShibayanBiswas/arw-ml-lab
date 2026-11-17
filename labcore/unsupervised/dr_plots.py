"""DR catalogue plots — scree, Shepard (§36 / 6B)."""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy.spatial.distance import pdist
from scipy.stats import spearmanr
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


def pca_scree(
    X: np.ndarray,
    *,
    seed: int = 42,
) -> dict[str, Any]:
    """DR.P.SCREE — eigenvalues on standardised data with Kaiser line (λ = 1)."""
    import plotly.graph_objects as go

    Xs = StandardScaler().fit_transform(np.asarray(X, dtype=float))
    n_comp = min(Xs.shape[1], max(1, Xs.shape[0] - 1))
    model = PCA(n_components=n_comp, random_state=seed)
    model.fit(Xs)
    eigenvalues = np.asarray(model.explained_variance_, dtype=float)
    evr = np.asarray(model.explained_variance_ratio_, dtype=float)
    cumulative = np.cumsum(evr)
    comps = list(range(1, len(eigenvalues) + 1))
    kaiser_k = int(np.sum(eigenvalues > 1.0))
    markers = (80.0, 90.0, 95.0)
    k_at: dict[str, int | None] = {}
    for pct in markers:
        hit = np.where(cumulative * 100.0 >= pct)[0]
        k_at[f"k_at_{int(pct)}pct"] = int(hit[0] + 1) if len(hit) else None

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=comps, y=eigenvalues.tolist(), mode="lines+markers", name="eigenvalue"))
    fig.add_hline(y=1.0, line_dash="dash", annotation_text="Kaiser (λ=1)")
    fig.update_layout(
        title=f"Scree (Kaiser k={kaiser_k})",
        xaxis_title="Component",
        yaxis_title="Eigenvalue (standardised PCA)",
        height=400,
    )
    return {
        "id": "DR.P.SCREE",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {
            "component": comps,
            "eigenvalue": [float(v) for v in eigenvalues],
            "explained_variance_ratio": [float(v) for v in evr],
            "cumulative_variance_ratio": [float(v) for v in cumulative],
            "kaiser_k": kaiser_k,
            **k_at,
        },
        "seed": seed,
    }


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
