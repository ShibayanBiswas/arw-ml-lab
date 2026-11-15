"""CV fold visualiser — Plotly artefact."""

from __future__ import annotations

from typing import Any

import numpy as np


def plot_cv_folds(
    fold_indices: list[tuple[np.ndarray, np.ndarray]],
    *,
    title: str = "CV folds",
    gap: int = 0,
) -> dict[str, Any]:
    """Show train/val membership per fold index (and optional gap band)."""
    import plotly.graph_objects as go

    fig = go.Figure()
    for i, (tr, va) in enumerate(fold_indices):
        fig.add_trace(
            go.Scatter(
                x=tr,
                y=np.full(len(tr), i),
                mode="markers",
                marker={"size": 4, "color": "#2a6"},
                name=f"fold{i} train",
                showlegend=(i == 0),
                legendgroup="train",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=va,
                y=np.full(len(va), i),
                mode="markers",
                marker={"size": 4, "color": "#c9a227"},
                name=f"fold{i} val",
                showlegend=(i == 0),
                legendgroup="val",
            )
        )
        if gap > 0 and len(va):
            g0 = int(np.min(va)) - gap
            g1 = int(np.min(va))
            fig.add_vrect(x0=g0, x1=g1, fillcolor="rgba(200,80,80,0.15)", line_width=0)
    fig.update_layout(
        title=title,
        xaxis_title="Sample index",
        yaxis_title="Fold",
        height=320 + 20 * len(fold_indices),
    )
    return {
        "id": "CV.P.FOLDS",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {"n_folds": len(fold_indices), "gap": gap},
    }


def iter_splits(
    splitter: Any,
    X: Any,
    y: Any | None = None,
    groups: Any | None = None,
) -> list[tuple[np.ndarray, np.ndarray]]:
    if splitter is None:
        return []
    kwargs: dict[str, Any] = {}
    if groups is not None:
        kwargs["groups"] = groups
    if y is not None:
        try:
            return [(tr, va) for tr, va in splitter.split(X, y, **kwargs)]
        except TypeError:
            return [(tr, va) for tr, va in splitter.split(X, **kwargs)]
    return [(tr, va) for tr, va in splitter.split(X, **kwargs)]
