"""Anomaly detection catalogue plots (§36 / 6B thin)."""

from __future__ import annotations

from typing import Any

import numpy as np


def anomaly_score_hist(
    scores: np.ndarray,
    *,
    threshold: float | None = None,
    is_outlier: np.ndarray | None = None,
    plot_id: str = "ANO.P.SCORE_HIST",
) -> dict[str, Any]:
    """Histogram of anomaly scores with optional threshold line."""
    import plotly.graph_objects as go

    s = np.asarray(scores, dtype=float)
    fig = go.Figure()
    out_mask = None
    if is_outlier is not None:
        out = np.asarray(is_outlier, dtype=int)
        if len(out) != len(s):
            raise ValueError("is_outlier must match scores length")
        out_mask = out == 1
        inlier = ~out_mask
        if np.any(inlier):
            fig.add_trace(go.Histogram(x=s[inlier], nbinsx=30, name="inlier", opacity=0.75))
        if np.any(out_mask):
            fig.add_trace(go.Histogram(x=s[out_mask], nbinsx=30, name="flagged", opacity=0.85))
        fig.update_layout(barmode="overlay")
    else:
        fig.add_trace(go.Histogram(x=s, nbinsx=30, name="score"))
    if threshold is not None:
        fig.add_vline(x=float(threshold), line_dash="dash", line_color="#c9a227")
    fig.update_layout(title="Anomaly score distribution", xaxis_title="Score", height=360)

    n_above = int((s >= threshold).sum()) if threshold is not None else None
    sep = None
    if out_mask is not None and np.any(out_mask) and np.any(~out_mask):
        pooled = float(np.nanstd(s, ddof=1)) if len(s) > 1 else None
        if pooled and pooled > 0:
            sep = (float(np.mean(s[out_mask]) - np.mean(s[~out_mask])) / pooled)

    numbers: dict[str, Any] = {
        "mean": float(np.nanmean(s)),
        "std": float(np.nanstd(s, ddof=1)) if len(s) > 1 else None,
        "threshold": threshold,
        "n_above_threshold": n_above,
    }
    if out_mask is not None:
        numbers["n_flagged"] = int(out_mask.sum())
        numbers["n_inlier"] = int((~out_mask).sum())
        numbers["score_separation_cohens_d"] = sep

    return {
        "id": plot_id,
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": numbers,
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


def _rank_elbow(ranks: np.ndarray, scores: np.ndarray) -> int | None:
    """Rank at maximum perpendicular distance from the rank–score chord (elbow heuristic)."""
    n = len(scores)
    if n < 3:
        return None
    x0, y0 = 1.0, float(scores[0])
    x1, y1 = float(n), float(scores[-1])
    dx, dy = x1 - x0, y1 - y0
    denom = float(np.hypot(dx, dy))
    if denom == 0:
        return None
    dist = np.abs(dy * ranks - dx * scores + x1 * y0 - y1 * x0) / denom
    return int(ranks[int(np.argmax(dist))])


def anomaly_pareto_rank(
    scores: np.ndarray,
    *,
    threshold: float | None = None,
    plot_id: str = "ANO.P.PARETO",
) -> dict[str, Any]:
    """Ranked score curve with cumulative score mass (Pareto / elbow view)."""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    s = np.asarray(scores, dtype=float)
    n = len(s)
    if n == 0:
        raise ValueError("scores must be non-empty")
    order = np.argsort(-s, kind="stable")
    ranked = s[order]
    ranks = np.arange(1, n + 1, dtype=float)
    total = float(np.sum(np.clip(ranked, 0.0, None)))
    if total > 0:
        cum_pct = np.cumsum(np.clip(ranked, 0.0, None)) / total * 100.0
    else:
        cum_pct = np.linspace(100.0 / n, 100.0, n)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=ranks,
            y=ranked,
            mode="lines+markers",
            name="score",
            marker=dict(size=4),
            hovertemplate="rank %{x}<br>score %{y:.4f}<br>index %{customdata}<extra></extra>",
            customdata=order,
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=ranks,
            y=cum_pct,
            mode="lines",
            name="cumulative %",
            line=dict(dash="dot", color="#c9a227"),
            hovertemplate="rank %{x}<br>cumulative %{y:.1f}%<extra></extra>",
        ),
        secondary_y=True,
    )
    if threshold is not None:
        fig.add_hline(y=float(threshold), line_dash="dash", line_color="#7f8c8d", secondary_y=False)
    elbow_rank = _rank_elbow(ranks, ranked)
    if elbow_rank is not None:
        fig.add_vline(
            x=float(elbow_rank),
            line_dash="dot",
            line_color="#c9a227",
            annotation_text="elbow",
        )
    fig.update_xaxes(title_text="Rank (1 = most anomalous)")
    fig.update_yaxes(title_text="Anomaly score", secondary_y=False)
    fig.update_yaxes(title_text="Cumulative % of score mass", secondary_y=True, range=[0, 105])
    fig.update_layout(title="Ranked anomaly scores (Pareto)", height=400)

    elbow_idx = elbow_rank - 1 if elbow_rank is not None else None
    return {
        "id": plot_id,
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {
            "n": n,
            "rank": ranks.astype(int).tolist(),
            "row_index": order.tolist(),
            "score": [float(v) for v in ranked],
            "cumulative_pct": [float(v) for v in cum_pct],
            "elbow_rank": elbow_rank,
            "elbow_score": float(ranked[elbow_idx]) if elbow_idx is not None else None,
            "threshold": threshold,
            "score_at_threshold_rank": (
                int(np.argmax(ranked >= threshold) + 1)
                if threshold is not None and np.any(ranked >= threshold)
                else None
            ),
        },
    }


def _top_features_by_score_corr(
    X: np.ndarray,
    scores: np.ndarray,
    *,
    top_k: int,
    feature_names: list[str] | None,
) -> tuple[list[str], list[float]]:
    """Rank features by |Pearson r| with anomaly scores (scipy.stats.pearsonr)."""
    from scipy.stats import pearsonr

    n_feat = X.shape[1]
    names = feature_names if feature_names is not None else [f"f{j}" for j in range(n_feat)]
    if len(names) != n_feat:
        raise ValueError("feature_names must match X column count")
    corrs: list[tuple[int, float]] = []
    sc = np.asarray(scores, dtype=float)
    for j in range(n_feat):
        col = np.asarray(X[:, j], dtype=float)
        if np.nanstd(col) == 0 or np.nanstd(sc) == 0:
            corrs.append((j, 0.0))
            continue
        r, _ = pearsonr(col, sc)
        corrs.append((j, float(r) if np.isfinite(r) else 0.0))
    corrs.sort(key=lambda t: abs(t[1]), reverse=True)
    k = min(max(2, top_k), n_feat)
    picked = corrs[:k]
    return [names[i] for i, _ in picked], [r for _, r in picked]


def anomaly_pairwise_feature_scatter(
    X: np.ndarray,
    scores: np.ndarray,
    is_outlier: np.ndarray,
    *,
    feature_names: list[str] | None = None,
    top_k: int = 4,
    plot_id: str = "ANO.P.PAIRWISE",
) -> dict[str, Any]:
    """Pairwise scatter of top |score|-correlated features; flag anomalies (§36.7)."""
    import pandas as pd
    import plotly.express as px

    X_arr = np.asarray(X, dtype=float)
    sc = np.asarray(scores, dtype=float)
    out = np.asarray(is_outlier, dtype=int)
    if X_arr.shape[0] != len(sc) or X_arr.shape[0] != len(out):
        raise ValueError("X, scores, and is_outlier must have the same number of rows")
    if X_arr.shape[0] < 2:
        raise ValueError("need at least two rows")
    if X_arr.shape[1] < 2:
        raise ValueError("need at least two features")

    sel_names, sel_corrs = _top_features_by_score_corr(
        X_arr, sc, top_k=top_k, feature_names=feature_names
    )
    n_feat = X_arr.shape[1]
    base_names = feature_names if feature_names is not None else [f"f{j}" for j in range(n_feat)]
    col_idx = [base_names.index(n) for n in sel_names]

    group = np.where(out == 1, "flagged", "inlier")
    data: dict[str, Any] = {"group": group, "score": sc}
    for name, j in zip(sel_names, col_idx, strict=True):
        data[name] = X_arr[:, j]
    df = pd.DataFrame(data)

    fig = px.scatter_matrix(
        df,
        dimensions=sel_names,
        color="group",
        color_discrete_map={"inlier": "#4a6fa5", "flagged": "#c0392b"},
        opacity=0.65,
        height=min(220 * len(sel_names) + 80, 900),
        width=min(220 * len(sel_names) + 80, 900),
        labels={c: c for c in sel_names},
        title="Pairwise scatter (top score-linked features)",
    )
    fig.update_traces(diagonal_visible=False, showupperhalf=False, marker=dict(size=6))
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02))

    inlier = out == 0
    flagged = out == 1
    sep = None
    if np.any(inlier) and np.any(flagged):
        pooled = float(np.nanstd(sc, ddof=1)) if len(sc) > 1 else None
        if pooled and pooled > 0:
            sep = float(np.mean(sc[flagged]) - np.mean(sc[inlier])) / pooled

    return {
        "id": plot_id,
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {
            "top_k": len(sel_names),
            "feature": sel_names,
            "score_correlation": sel_corrs,
            "n_flagged": int(flagged.sum()),
            "n_inlier": int(inlier.sum()),
            "n_pairs": len(sel_names) * (len(sel_names) - 1) // 2,
            "score_separation_cohens_d": sep,
        },
    }
