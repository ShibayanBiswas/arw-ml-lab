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
