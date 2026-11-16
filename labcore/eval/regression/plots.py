"""Minimum REE.P residual plots — Plotly."""

from __future__ import annotations

from typing import Any

import numpy as np


def plot_pred_vs_actual(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, Any]:
    import plotly.graph_objects as go

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=y_true, y=y_pred, mode="markers", name="points", opacity=0.6))
    lo = float(min(np.min(y_true), np.min(y_pred)))
    hi = float(max(np.max(y_true), np.max(y_pred)))
    fig.add_trace(
        go.Scatter(x=[lo, hi], y=[lo, hi], mode="lines", name="y=x", line={"dash": "dash"})
    )
    fig.update_layout(
        title="Predicted vs actual", xaxis_title="Actual", yaxis_title="Predicted", height=400
    )
    return {"id": "REE.P.PRED_VS_ACTUAL", "kind": "plot", "plotly": fig.to_plotly_json()}


def plot_residual_scatter(y_pred: np.ndarray, resid: np.ndarray) -> dict[str, Any]:
    import plotly.graph_objects as go

    fig = go.Figure(go.Scatter(x=y_pred, y=resid, mode="markers", opacity=0.6))
    fig.add_hline(y=0, line_dash="dash")
    fig.update_layout(
        title="Residuals vs fitted", xaxis_title="Fitted", yaxis_title="Residual", height=400
    )
    return {"id": "REE.P.RESID_SCATTER", "kind": "plot", "plotly": fig.to_plotly_json()}


def plot_residual_hist(resid: np.ndarray) -> dict[str, Any]:
    import plotly.graph_objects as go

    fig = go.Figure(go.Histogram(x=resid, nbinsx=30))
    fig.update_layout(title="Residual histogram", xaxis_title="Residual", height=400)
    return {"id": "REE.P.RESID_HIST", "kind": "plot", "plotly": fig.to_plotly_json()}


def plot_qq(resid: np.ndarray) -> dict[str, Any]:
    import plotly.graph_objects as go
    from scipy import stats

    (osm, osr), (slope, intercept, _r) = stats.probplot(resid, dist="norm")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=osm, y=osr, mode="markers", name="sample"))
    fit_y = slope * np.asarray(osm) + intercept
    fig.add_trace(go.Scatter(x=osm, y=fit_y, mode="lines", name="fit"))
    fig.update_layout(
        title="Normal Q-Q", xaxis_title="Theoretical", yaxis_title="Sample", height=400
    )
    return {"id": "REE.P.QQ", "kind": "plot", "plotly": fig.to_plotly_json()}


def plot_cooks_distance(cooks: np.ndarray) -> dict[str, Any]:
    import plotly.graph_objects as go

    idx = np.arange(len(cooks))
    fig = go.Figure(go.Scatter(x=idx, y=cooks, mode="markers", name="Cook's D"))
    fig.update_layout(
        title="Cook's distance", xaxis_title="Index", yaxis_title="Cook's D", height=400
    )
    return {"id": "REE.P.COOKS", "kind": "plot", "plotly": fig.to_plotly_json()}


def plot_studentised_residuals(stud: np.ndarray) -> dict[str, Any]:
    import plotly.graph_objects as go

    idx = np.arange(len(stud))
    fig = go.Figure(go.Scatter(x=idx, y=stud, mode="markers", name="studentised"))
    fig.add_hline(y=0, line_dash="dash")
    fig.update_layout(
        title="Studentised residuals",
        xaxis_title="Index",
        yaxis_title="Studentised residual",
        height=400,
    )
    return {"id": "REE.P.STUD_RESID", "kind": "plot", "plotly": fig.to_plotly_json()}


def plot_bland_altman(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, Any]:
    import plotly.graph_objects as go

    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    mean = (y_true + y_pred) / 2.0
    diff = y_pred - y_true
    md = float(np.mean(diff))
    sd = float(np.std(diff, ddof=1))
    fig = go.Figure(go.Scatter(x=mean, y=diff, mode="markers", opacity=0.6))
    fig.add_hline(y=md, line_dash="solid")
    fig.add_hline(y=md + 1.96 * sd, line_dash="dash")
    fig.add_hline(y=md - 1.96 * sd, line_dash="dash")
    fig.update_layout(
        title="Bland–Altman",
        xaxis_title="Mean of actual & predicted",
        yaxis_title="Predicted − actual",
        height=400,
    )
    return {
        "id": "REE.P.BLAND_ALTMAN",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {"mean_diff": md, "sd": sd},
    }


def plot_residual_acf(resid: np.ndarray, nlags: int = 20) -> dict[str, Any]:
    import plotly.graph_objects as go
    from statsmodels.tsa.stattools import acf

    resid = np.asarray(resid, dtype=float)
    nlags = min(nlags, max(1, len(resid) // 2 - 1))
    vals = acf(resid, nlags=nlags, fft=True)
    fig = go.Figure(go.Bar(x=list(range(len(vals))), y=vals, name="ACF"))
    fig.update_layout(title="Residual ACF", xaxis_title="Lag", yaxis_title="ACF", height=400)
    return {"id": "REE.P.RESID_ACF", "kind": "plot", "plotly": fig.to_plotly_json()}


def plot_abs_resid_vs_fitted(y_pred: np.ndarray, resid: np.ndarray) -> dict[str, Any]:
    """REE.P.ABS_RESID — |residual| vs fitted (heteroscedasticity visual)."""
    import plotly.graph_objects as go

    fig = go.Figure(
        go.Scatter(x=y_pred, y=np.abs(np.asarray(resid, dtype=float)), mode="markers", opacity=0.55)
    )
    fig.update_layout(
        title="|Residual| vs fitted",
        xaxis_title="Fitted",
        yaxis_title="|Residual|",
        height=400,
    )
    return {"id": "REE.P.ABS_RESID", "kind": "plot", "plotly": fig.to_plotly_json()}


def plot_error_hist(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, Any]:
    """REE.P.ERROR_HIST — prediction error histogram."""
    import plotly.graph_objects as go

    err = np.asarray(y_pred, dtype=float) - np.asarray(y_true, dtype=float)
    fig = go.Figure(go.Histogram(x=err, nbinsx=30))
    fig.update_layout(title="Prediction error", xaxis_title="pred − actual", height=400)
    return {"id": "REE.P.ERROR_HIST", "kind": "plot", "plotly": fig.to_plotly_json()}


def plot_rec(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, Any]:
    """REE.P.REC — regression error characteristic (share with |e|≤ε vs ε)."""
    import plotly.graph_objects as go

    err = np.abs(np.asarray(y_pred, dtype=float) - np.asarray(y_true, dtype=float))
    eps = np.linspace(0, float(np.nanmax(err)) if len(err) else 1.0, 50)
    share = np.array([(err <= e).mean() for e in eps], dtype=float)
    area = float(np.trapezoid(share, eps)) if len(eps) > 1 else 0.0
    fig = go.Figure(go.Scatter(x=eps, y=share, mode="lines", name="REC"))
    fig.update_layout(
        title=f"REC (area={area:.3g})",
        xaxis_title="ε",
        yaxis_title="Share |e|≤ε",
        height=400,
    )
    return {
        "id": "REE.P.REC",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {"area": area},
    }


def plot_cum_error(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, Any]:
    """REE.P.CUM_ERROR — cumulative share of |e| vs share of rows."""
    import plotly.graph_objects as go

    err = np.abs(np.asarray(y_pred, dtype=float) - np.asarray(y_true, dtype=float))
    order = np.argsort(-err)
    cum = np.cumsum(err[order])
    total = max(float(cum[-1]) if len(cum) else 1.0, 1e-12)
    x = np.arange(1, len(cum) + 1) / max(len(cum), 1)
    y = cum / total
    fig = go.Figure(go.Scatter(x=x, y=y, mode="lines", name="cum |e|"))
    fig.update_layout(
        title="Cumulative absolute error",
        xaxis_title="Share of rows (worst first)",
        yaxis_title="Share of total |e|",
        height=400,
    )
    return {"id": "REE.P.CUM_ERROR", "kind": "plot", "plotly": fig.to_plotly_json()}


def plot_scale_location(y_pred: np.ndarray, resid: np.ndarray) -> dict[str, Any]:
    """REE.P.SCALE_LOCATION — √|standardised residual| vs fitted."""
    import plotly.graph_objects as go

    resid = np.asarray(resid, dtype=float)
    sd = float(np.nanstd(resid, ddof=1)) or 1.0
    stud = resid / sd
    y = np.sqrt(np.abs(stud))
    fig = go.Figure(go.Scatter(x=y_pred, y=y, mode="markers", opacity=0.55))
    fig.update_layout(
        title="Scale-location",
        xaxis_title="Fitted",
        yaxis_title="√|standardised residual|",
        height=400,
    )
    return {"id": "REE.P.SCALE_LOCATION", "kind": "plot", "plotly": fig.to_plotly_json()}
