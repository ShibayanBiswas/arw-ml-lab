"""Anomaly detection catalogue plots (§36 / 6B thin)."""

from __future__ import annotations

from typing import Any

import numpy as np


def anomaly_score_hist(
    scores: np.ndarray,
    *,
    threshold: float | None = None,
    plot_id: str = "ANO.P.SCORE_HIST",
) -> dict[str, Any]:
    """Histogram of anomaly scores with optional threshold line."""
    import plotly.graph_objects as go

    s = np.asarray(scores, dtype=float)
    fig = go.Figure(go.Histogram(x=s, nbinsx=30, name="score"))
    if threshold is not None:
        fig.add_vline(x=float(threshold), line_dash="dash")
    fig.update_layout(title="Anomaly score distribution", xaxis_title="Score", height=360)
    return {
        "id": plot_id,
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {
            "mean": float(np.nanmean(s)),
            "std": float(np.nanstd(s, ddof=1)) if len(s) > 1 else None,
            "threshold": threshold,
        },
    }


def anomaly_ranked_bar(
    scores: np.ndarray,
    *,
    top_n: int = 20,
    plot_id: str = "ANO.P.RANKED",
) -> dict[str, Any]:
    """Horizontal bar chart of highest anomaly scores (rank 1 = most anomalous)."""
    import plotly.graph_objects as go

    s = np.asarray(scores, dtype=float)
    n = len(s)
    if n == 0:
        raise ValueError("scores must be non-empty")
    k = min(max(1, top_n), n)
    order = np.argsort(-s, kind="stable")[:k]
    ranked_scores = s[order]
    ranks = list(range(1, k + 1))
    percentiles = [float(100.0 * (n - i) / n) for i in order]

    fig = go.Figure(
        go.Bar(
            x=ranked_scores.tolist(),
            y=[f"#{r}" for r in ranks],
            orientation="h",
            text=[f"{v:.3f}" for v in ranked_scores],
            textposition="outside",
            hovertemplate="rank %{y}<br>score %{x:.4f}<br>index %{customdata}<extra></extra>",
            customdata=order.tolist(),
        )
    )
    fig.update_layout(
        title=f"Top {k} anomaly scores",
        xaxis_title="Score (higher = more anomalous)",
        yaxis_title="Rank",
        height=max(320, 28 * k + 80),
        yaxis=dict(categoryorder="array", categoryarray=[f"#{r}" for r in reversed(ranks)]),
    )
    return {
        "id": plot_id,
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {
            "top_n": k,
            "rank": ranks,
            "row_index": order.tolist(),
            "score": [float(v) for v in ranked_scores],
            "percentile": percentiles,
        },
    }


def anomaly_embedding_scatter(
    X: np.ndarray,
    scores: np.ndarray,
    is_outlier: np.ndarray,
    *,
    seed: int = 42,
    plot_id: str = "ANO.P.EMBED",
) -> dict[str, Any]:
    """PCA 2D embedding with inliers vs flagged anomalies highlighted."""
    import plotly.graph_objects as go
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler

    X_arr = np.asarray(X, dtype=float)
    sc = np.asarray(scores, dtype=float)
    out = np.asarray(is_outlier, dtype=int)
    if X_arr.shape[0] != len(sc) or X_arr.shape[0] != len(out):
        raise ValueError("X, scores, and is_outlier must have the same number of rows")
    if X_arr.shape[0] < 2:
        raise ValueError("need at least two rows")

    Xs = StandardScaler().fit_transform(X_arr)
    n_comp = min(2, Xs.shape[1])
    pca = PCA(n_components=n_comp, random_state=seed)
    coords = pca.fit_transform(Xs)
    evr = np.asarray(pca.explained_variance_ratio_, dtype=float)
    pc_x = coords[:, 0]
    pc_y = coords[:, 1] if n_comp > 1 else np.zeros_like(pc_x)

    inlier = out == 0
    flagged = out == 1
    fig = go.Figure()
    if np.any(inlier):
        fig.add_trace(
            go.Scatter(
                x=pc_x[inlier],
                y=pc_y[inlier],
                mode="markers",
                name="inlier",
                marker=dict(
                    size=7,
                    opacity=0.55,
                    color=sc[inlier],
                    colorscale="Blues",
                    showscale=False,
                ),
                text=[f"#{i}" for i in np.where(inlier)[0]],
                hovertemplate=(
                    "row %{text}<br>PC1 %{x:.3f}<br>PC2 %{y:.3f}"
                    "<br>score %{customdata:.4f}<extra></extra>"
                ),
                customdata=sc[inlier],
            )
        )
    if np.any(flagged):
        fig.add_trace(
            go.Scatter(
                x=pc_x[flagged],
                y=pc_y[flagged],
                mode="markers",
                name="flagged",
                marker=dict(size=11, color="#c0392b", line=dict(width=1, color="#2c1810")),
                text=[f"#{i}" for i in np.where(flagged)[0]],
                hovertemplate=(
                    "row %{text}<br>PC1 %{x:.3f}<br>PC2 %{y:.3f}"
                    "<br>score %{customdata:.4f}<extra></extra>"
                ),
                customdata=sc[flagged],
            )
        )
    x_lab = f"PC1 ({100.0 * evr[0]:.1f}% var)" if len(evr) else "PC1"
    y_lab = f"PC2 ({100.0 * evr[1]:.1f}% var)" if len(evr) > 1 else "PC2"
    fig.update_layout(
        title="Anomaly scores on PCA embedding",
        xaxis_title=x_lab,
        yaxis_title=y_lab,
        height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )

    sep = None
    if np.any(inlier) and np.any(flagged):
        pooled = float(np.nanstd(sc, ddof=1)) if len(sc) > 1 else None
        if pooled and pooled > 0:
            sep = (float(np.mean(sc[flagged]) - np.mean(sc[inlier])) / pooled)

    return {
        "id": plot_id,
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {
            "n_flagged": int(flagged.sum()),
            "n_inlier": int(inlier.sum()),
            "explained_variance_ratio_pc1": float(evr[0]) if len(evr) else None,
            "explained_variance_ratio_pc2": float(evr[1]) if len(evr) > 1 else None,
            "score_separation_cohens_d": sep,
        },
        "seed": seed,
    }
