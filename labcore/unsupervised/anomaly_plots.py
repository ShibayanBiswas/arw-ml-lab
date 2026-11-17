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
