"""Minimum CLE.P set for Eval Core — Plotly JSON from library numbers."""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.calibration import calibration_curve
from sklearn.metrics import precision_recall_curve, roc_curve


def plot_confusion(
    cm: list[list[float]],
    labels: list[str],
    *,
    title: str,
    plot_id: str = "CLE.P.CM",
) -> dict[str, Any]:
    import plotly.graph_objects as go

    z = np.asarray(cm, dtype=float)
    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=[str(l) for l in labels],
            y=[str(l) for l in labels],
            colorscale="Blues",
            text=z,
            texttemplate="%{text:.3g}",
        )
    )
    fig.update_layout(title=title, xaxis_title="Predicted", yaxis_title="True", height=420)
    return {"id": plot_id, "kind": "plot", "name": title, "plotly": fig.to_plotly_json()}


def plot_roc(y_true: np.ndarray, scores: np.ndarray) -> dict[str, Any]:
    import plotly.graph_objects as go
    from sklearn.metrics import auc

    fpr, tpr, _ = roc_curve(y_true, scores)
    a = auc(fpr, tpr)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=fpr, y=tpr, mode="lines", name=f"ROC AUC={a:.3f}"))
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="chance", line={"dash": "dash"}))
    fig.update_layout(title="ROC", xaxis_title="FPR", yaxis_title="TPR", height=400)
    return {"id": "CLE.P.ROC", "kind": "plot", "plotly": fig.to_plotly_json(), "numbers": {"auc": float(a)}}


def plot_pr(y_true: np.ndarray, scores: np.ndarray) -> dict[str, Any]:
    import plotly.graph_objects as go
    from sklearn.metrics import average_precision_score

    p, r, _ = precision_recall_curve(y_true, scores)
    ap = float(average_precision_score(y_true, scores))
    fig = go.Figure(go.Scatter(x=r, y=p, mode="lines", name=f"AP={ap:.3f}"))
    fig.update_layout(title="Precision-Recall", xaxis_title="Recall", yaxis_title="Precision", height=400)
    return {"id": "CLE.P.PR", "kind": "plot", "plotly": fig.to_plotly_json(), "numbers": {"ap": ap}}


def plot_reliability(y_true: np.ndarray, scores: np.ndarray) -> dict[str, Any]:
    import plotly.graph_objects as go

    frac_pos, mean_pred = calibration_curve(y_true, scores, n_bins=10, strategy="uniform")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=mean_pred, y=frac_pos, mode="lines+markers", name="model"))
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="perfect", line={"dash": "dash"}))
    fig.update_layout(title="Reliability", xaxis_title="Mean predicted", yaxis_title="Fraction positive", height=400)
    return {"id": "CLE.P.RELIABILITY", "kind": "plot", "plotly": fig.to_plotly_json()}
