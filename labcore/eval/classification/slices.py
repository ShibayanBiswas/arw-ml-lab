"""CLE.P.SLICES / CLE.T.SLICES — metric by segment via fairlearn MetricFrame."""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.metrics import accuracy_score, f1_score, recall_score


def metric_by_segment(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    segment: np.ndarray,
    *,
    seed: int = 42,
) -> dict[str, Any]:
    """Group metrics by a discrete segment column (library MetricFrame)."""
    from fairlearn.metrics import MetricFrame

    _ = seed
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    segment = np.asarray(segment)
    avg_mode = "binary" if len(np.unique(y_true)) == 2 else "macro"
    mf = MetricFrame(
        metrics={
            "accuracy": accuracy_score,
            "f1": lambda yt, yp: f1_score(yt, yp, zero_division=np.nan, average=avg_mode),
            "recall": lambda yt, yp: recall_score(yt, yp, zero_division=np.nan, average=avg_mode),
        },
        y_true=y_true,
        y_pred=y_pred,
        sensitive_features=segment,
    )
    by_group = mf.by_group.reset_index()
    by_group.columns = ["segment"] + list(by_group.columns[1:])
    rows = by_group.to_dict(orient="records")
    overall = {k: float(v) if v == v else None for k, v in mf.overall.items()}

    import plotly.graph_objects as go

    segs = [str(r["segment"]) for r in rows]
    metric_colors = {"accuracy": "#1f77b4", "f1": "#ff7f0e", "recall": "#2ca02c"}
    fig = go.Figure()
    for metric in ("accuracy", "f1", "recall"):
        fig.add_trace(
            go.Bar(
                x=segs,
                y=[float(r[metric]) if r.get(metric) == r.get(metric) else None for r in rows],
                name=metric,
                marker_color=metric_colors[metric],
            )
        )
        ov = overall.get(metric)
        if ov is not None and ov == ov:
            fig.add_hline(
                y=ov,
                line_dash="dot",
                line_color=metric_colors[metric],
                annotation_text=f"overall {metric}",
                annotation_position="right",
            )
    fig.update_layout(
        title="Metrics by segment",
        barmode="group",
        height=420,
        yaxis=dict(range=[0, 1.05], title="Score"),
        xaxis_title="Segment",
    )
    plot_numbers = {
        "averaging": avg_mode,
        "overall": overall,
        "by_segment": {
            str(r["segment"]): {k: r.get(k) for k in ("accuracy", "f1", "recall")}
            for r in rows
        },
    }
    return {
        "id": "CLE.T.SLICES",
        "kind": "table",
        "rows": rows,
        "overall": overall,
        "plots": [
            {
                "id": "CLE.P.SLICES",
                "kind": "plot",
                "plotly": fig.to_plotly_json(),
                "numbers": plot_numbers,
            }
        ],
    }
