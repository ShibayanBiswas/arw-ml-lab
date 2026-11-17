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


def pca_cumulative_variance(
    X: np.ndarray,
    *,
    seed: int = 42,
) -> dict[str, Any]:
    """DR.P.CUMVAR — cumulative explained variance with 80/90/95% markers."""
    import plotly.graph_objects as go

    Xs = StandardScaler().fit_transform(np.asarray(X, dtype=float))
    n_comp = min(Xs.shape[1], max(1, Xs.shape[0] - 1))
    model = PCA(n_components=n_comp, random_state=seed)
    model.fit(Xs)
    evr = np.asarray(model.explained_variance_ratio_, dtype=float)
    cumulative = np.cumsum(evr)
    comps = list(range(1, len(evr) + 1))
    cum_pct = (cumulative * 100.0).tolist()
    markers = (80.0, 90.0, 95.0)
    k_at: dict[str, int | None] = {}
    for pct in markers:
        hit = np.where(cumulative * 100.0 >= pct)[0]
        k_at[f"k_at_{int(pct)}pct"] = int(hit[0] + 1) if len(hit) else None

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=comps, y=cum_pct, mode="lines+markers", name="cumulative %"),
    )
    for pct in markers:
        fig.add_hline(
            y=pct,
            line_dash="dash",
            annotation_text=f"{int(pct)}%",
        )
        kk = k_at[f"k_at_{int(pct)}pct"]
        if kk is not None:
            fig.add_vline(x=kk, line_dash="dot", opacity=0.35)
    title_bits = ", ".join(f"{int(p)}%→k={k_at[f'k_at_{int(p)}pct']}" for p in markers)
    fig.update_layout(
        title=f"Cumulative variance ({title_bits})",
        xaxis_title="Number of components (k)",
        yaxis_title="Cumulative explained variance (%)",
        yaxis_range=[0, 100.5],
        height=400,
    )
    return {
        "id": "DR.P.CUMVAR",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {
            "component": comps,
            "explained_variance_ratio": [float(v) for v in evr],
            "cumulative_variance_pct": [float(v) for v in cum_pct],
            **k_at,
        },
        "seed": seed,
    }


def pca_biplot(
    X: np.ndarray,
    *,
    feature_names: list[str] | None = None,
    pc_x: int = 1,
    pc_y: int = 2,
    seed: int = 42,
    loading_threshold: float = 0.4,
) -> dict[str, Any]:
    """DR.P.BIPLOT — PCA scores on PC_i × PC_j with loading arrows (|loading| > threshold highlighted)."""
    import plotly.graph_objects as go

    X = np.asarray(X, dtype=float)
    n_features = X.shape[1]
    if pc_x == pc_y:
        raise ValueError("pc_x and pc_y must differ")
    if not (1 <= pc_x <= n_features and 1 <= pc_y <= n_features):
        raise ValueError("pc_x and pc_y must be within [1, n_features]")

    names = feature_names or [f"f{j}" for j in range(n_features)]
    if len(names) != n_features:
        raise ValueError("feature_names length must match n_features")

    Xs = StandardScaler().fit_transform(X)
    n_comp = min(Xs.shape[1], max(1, Xs.shape[0] - 1))
    model = PCA(n_components=n_comp, random_state=seed)
    scores = model.fit_transform(Xs)
    ev = np.asarray(model.explained_variance_, dtype=float)
    loadings = (model.components_.T * np.sqrt(ev)).astype(float)
    ix, iy = pc_x - 1, pc_y - 1

    sx = scores[:, ix]
    sy = scores[:, iy]
    lx = loadings[:, ix]
    ly = loadings[:, iy]
    arrow_scale = float(np.max(np.abs(np.c_[sx, sy]))) / max(float(np.max(np.abs(np.c_[lx, ly]))), 1e-12)
    lx_plot = (lx * arrow_scale).tolist()
    ly_plot = (ly * arrow_scale).tolist()
    strong = [abs(lx[j]) > loading_threshold or abs(ly[j]) > loading_threshold for j in range(n_features)]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=sx.tolist(),
            y=sy.tolist(),
            mode="markers",
            name="scores",
            opacity=0.65,
        )
    )
    for j in range(n_features):
        color = "#c9a227" if strong[j] else "rgba(120,120,120,0.75)"
        width = 2.5 if strong[j] else 1.25
        fig.add_trace(
            go.Scatter(
                x=[0.0, lx_plot[j]],
                y=[0.0, ly_plot[j]],
                mode="lines+markers+text",
                text=["", names[j]],
                textposition="top center",
                line=dict(color=color, width=width),
                marker=dict(size=[0, 6]),
                showlegend=False,
                hoverinfo="skip",
            )
        )
    evr = np.asarray(model.explained_variance_ratio_, dtype=float)
    fig.update_layout(
        title=f"Biplot PC{pc_x} × PC{pc_y} ({evr[ix] * 100:.1f}% / {evr[iy] * 100:.1f}% var)",
        xaxis_title=f"PC{pc_x}",
        yaxis_title=f"PC{pc_y}",
        height=480,
    )
    loading_mat = loadings.tolist()
    return {
        "id": "DR.P.BIPLOT",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {
            "pc_x": pc_x,
            "pc_y": pc_y,
            "explained_variance_ratio_pc_x": float(evr[ix]),
            "explained_variance_ratio_pc_y": float(evr[iy]),
            "loadings": [[float(v) for v in row] for row in loading_mat],
            "feature": names,
            "strong_loading_indices": [j for j, flag in enumerate(strong) if flag],
            "arrow_scale": arrow_scale,
            "loading_threshold": loading_threshold,
        },
        "seed": seed,
    }


def pca_loadings_heatmap(
    X: np.ndarray,
    *,
    feature_names: list[str] | None = None,
    seed: int = 42,
    loading_threshold: float = 0.4,
    max_components: int | None = None,
) -> dict[str, Any]:
    """DR.P.LOADINGS — variable × PC loadings heatmap (|loading| > threshold highlighted)."""
    import plotly.graph_objects as go

    X = np.asarray(X, dtype=float)
    n_features = X.shape[1]
    names = feature_names or [f"f{j}" for j in range(n_features)]
    if len(names) != n_features:
        raise ValueError("feature_names length must match n_features")

    Xs = StandardScaler().fit_transform(X)
    n_comp = min(Xs.shape[1], max(1, Xs.shape[0] - 1))
    model = PCA(n_components=n_comp, random_state=seed)
    model.fit(Xs)
    ev = np.asarray(model.explained_variance_, dtype=float)
    loadings = (model.components_.T * np.sqrt(ev)).astype(float)
    k_show = n_comp if max_components is None else min(n_comp, max(1, max_components))
    loadings = loadings[:, :k_show]
    pc_labels = [f"PC{i}" for i in range(1, k_show + 1)]
    strong = np.abs(loadings) > loading_threshold
    text = [
        [f"{loadings[j, i]:.2f}" for i in range(k_show)] for j in range(n_features)
    ]
    zmax = float(np.max(np.abs(loadings))) if loadings.size else 1.0
    zmax = max(zmax, loading_threshold, 0.01)

    fig = go.Figure(
        go.Heatmap(
            z=loadings.tolist(),
            x=pc_labels,
            y=names,
            zmid=0.0,
            zmin=-zmax,
            zmax=zmax,
            colorscale="RdBu",
            text=text,
            texttemplate="%{text}",
            hovertemplate="feature=%{y}<br>%{x}=%{z:.3f}<extra></extra>",
        )
    )
    n_strong = int(np.sum(strong))
    fig.update_layout(
        title=f"PCA loadings (|λ|>{loading_threshold}: {n_strong} cells)",
        xaxis_title="Component",
        yaxis_title="Feature",
        height=max(320, 28 * n_features + 120),
    )
    strong_cells = [
        {"feature": names[j], "pc": pc_labels[i], "loading": float(loadings[j, i])}
        for j in range(n_features)
        for i in range(k_show)
        if strong[j, i]
    ]
    return {
        "id": "DR.P.LOADINGS",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {
            "loadings": [[float(v) for v in row] for row in loadings.tolist()],
            "feature": names,
            "component": pc_labels,
            "strong_cells": strong_cells,
            "n_strong_cells": n_strong,
            "loading_threshold": loading_threshold,
            "n_components_shown": k_show,
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
