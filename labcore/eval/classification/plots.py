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


def plot_gains_lift(y_true: np.ndarray, scores: np.ndarray) -> list[dict[str, Any]]:
    """Cumulative gains + lift from ranked scores (library sort + thin arithmetic)."""
    import plotly.graph_objects as go

    y = np.asarray(y_true).astype(int)
    s = np.asarray(scores, dtype=float)
    order = np.argsort(-s)
    y_sorted = y[order]
    n = len(y_sorted)
    cum_pos = np.cumsum(y_sorted)
    total_pos = max(int(cum_pos[-1]), 1)
    pct = np.arange(1, n + 1) / n
    gains = cum_pos / total_pos
    baseline = pct
    lift = gains / np.maximum(baseline, 1e-12)
    fig_g = go.Figure()
    fig_g.add_trace(go.Scatter(x=pct, y=gains, mode="lines", name="model"))
    fig_g.add_trace(go.Scatter(x=pct, y=baseline, mode="lines", name="baseline", line={"dash": "dash"}))
    fig_g.update_layout(title="Cumulative gains", xaxis_title="% population", yaxis_title="% positives", height=400)
    fig_l = go.Figure(go.Scatter(x=pct, y=lift, mode="lines", name="lift"))
    fig_l.add_hline(y=1.0, line_dash="dash")
    fig_l.update_layout(title="Lift", xaxis_title="% population", yaxis_title="Lift", height=400)
    return [
        {"id": "CLE.P.GAINS", "kind": "plot", "plotly": fig_g.to_plotly_json()},
        {"id": "CLE.P.LIFT", "kind": "plot", "plotly": fig_l.to_plotly_json()},
    ]


def plot_ks(y_true: np.ndarray, scores: np.ndarray) -> dict[str, Any]:
    import plotly.graph_objects as go
    from scipy import stats

    y = np.asarray(y_true)
    s = np.asarray(scores, dtype=float)
    pos = s[y == 1] if set(np.unique(y)).issubset({0, 1}) else s[y == y.max()]
    neg = s[y == 0] if set(np.unique(y)).issubset({0, 1}) else s[y != y.max()]
    if len(pos) < 2 or len(neg) < 2:
        return {"id": "CLE.P.KS", "kind": "plot", "plotly": {}, "numbers": {"ks": None}}
    ks_stat, p = stats.ks_2samp(pos, neg)
    # ECDFs
    x = np.sort(np.concatenate([pos, neg]))
    ecdf_p = np.searchsorted(np.sort(pos), x, side="right") / len(pos)
    ecdf_n = np.searchsorted(np.sort(neg), x, side="right") / len(neg)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=ecdf_p, mode="lines", name="positive"))
    fig.add_trace(go.Scatter(x=x, y=ecdf_n, mode="lines", name="negative"))
    fig.update_layout(title=f"KS={ks_stat:.3f}", xaxis_title="Score", yaxis_title="ECDF", height=400)
    return {
        "id": "CLE.P.KS",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {"ks": float(ks_stat), "pvalue": float(p)},
    }


def plot_threshold_vs_metric(y_true: np.ndarray, scores: np.ndarray) -> dict[str, Any]:
    import plotly.graph_objects as go
    from sklearn.metrics import f1_score, precision_score, recall_score

    y = np.asarray(y_true)
    s = np.asarray(scores, dtype=float)
    thr = np.linspace(0.05, 0.95, 19)
    f1s, precs, recs = [], [], []
    for t in thr:
        pred = (s >= t).astype(int)
        f1s.append(float(f1_score(y, pred, zero_division=np.nan)))
        precs.append(float(precision_score(y, pred, zero_division=np.nan)))
        recs.append(float(recall_score(y, pred, zero_division=np.nan)))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=thr, y=f1s, mode="lines", name="F1"))
    fig.add_trace(go.Scatter(x=thr, y=precs, mode="lines", name="Precision"))
    fig.add_trace(go.Scatter(x=thr, y=recs, mode="lines", name="Recall"))
    fig.update_layout(title="Threshold vs metric", xaxis_title="Threshold", yaxis_title="Score", height=400)
    return {"id": "CLE.P.THRESHOLD", "kind": "plot", "plotly": fig.to_plotly_json()}


def plot_det(y_true: np.ndarray, scores: np.ndarray) -> dict[str, Any]:
    import plotly.graph_objects as go
    from sklearn.metrics import det_curve

    fpr, fnr, _ = det_curve(y_true, scores)
    fig = go.Figure(go.Scatter(x=fpr, y=fnr, mode="lines", name="DET"))
    fig.update_layout(title="DET", xaxis_title="FPR", yaxis_title="FNR", height=400)
    return {"id": "CLE.P.DET", "kind": "plot", "plotly": fig.to_plotly_json()}


def plot_prob_density_by_class(y_true: np.ndarray, scores: np.ndarray) -> dict[str, Any]:
    import plotly.graph_objects as go

    y = np.asarray(y_true)
    s = np.asarray(scores, dtype=float)
    fig = go.Figure()
    for lab in sorted(np.unique(y)):
        fig.add_trace(go.Histogram(x=s[y == lab], name=str(lab), opacity=0.55, nbinsx=30))
    fig.update_layout(
        title="Score density by class",
        barmode="overlay",
        xaxis_title="Score",
        height=400,
    )
    return {"id": "CLE.P.PROB_DENS", "kind": "plot", "plotly": fig.to_plotly_json()}


def plot_per_class_prf(y_true: np.ndarray, y_pred: np.ndarray, labels: list[Any] | None = None) -> dict[str, Any]:
    import plotly.graph_objects as go
    from sklearn.metrics import precision_recall_fscore_support

    labels = labels if labels is not None else sorted(np.unique(y_true).tolist())
    p, r, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, zero_division=np.nan
    )
    x = [str(l) for l in labels]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=x, y=p, name="Precision"))
    fig.add_trace(go.Bar(x=x, y=r, name="Recall"))
    fig.add_trace(go.Bar(x=x, y=f1, name="F1"))
    fig.update_layout(title="Per-class P/R/F1", barmode="group", height=400)
    return {"id": "CLE.P.PER_CLASS_PRF", "kind": "plot", "plotly": fig.to_plotly_json()}
