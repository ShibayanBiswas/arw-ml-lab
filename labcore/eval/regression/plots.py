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


def plot_target_pred_density(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, Any]:
    """REE.P.TARGET_PRED_DENSITY — KDE of y vs ŷ (scipy gaussian_kde)."""
    import plotly.graph_objects as go
    from scipy.stats import gaussian_kde

    yt = np.asarray(y_true, dtype=float)
    yp = np.asarray(y_pred, dtype=float)
    lo = float(np.nanmin([yt.min(), yp.min()]))
    hi = float(np.nanmax([yt.max(), yp.max()]))
    xs = np.linspace(lo, hi, 200)
    fig = go.Figure()
    for name, arr in (("y", yt), ("ŷ", yp)):
        try:
            kde = gaussian_kde(arr)
            fig.add_trace(go.Scatter(x=xs, y=kde(xs), mode="lines", name=name))
        except Exception:
            fig.add_trace(
                go.Histogram(x=arr, name=name, histnorm="probability density", opacity=0.5)
            )
    fig.update_layout(title="Target vs prediction density", height=360)
    return {"id": "REE.P.TARGET_PRED_DENSITY", "kind": "plot", "plotly": fig.to_plotly_json()}


def plot_pct_err_dist(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, Any]:
    """REE.P.PCT_ERR_DIST — percentage error clipped at ±100%."""
    import plotly.graph_objects as go

    yt = np.asarray(y_true, dtype=float)
    yp = np.asarray(y_pred, dtype=float)
    mask = np.isfinite(yt) & (np.abs(yt) > 1e-12)
    pct = np.clip(100.0 * (yp[mask] - yt[mask]) / yt[mask], -100.0, 100.0)
    fig = go.Figure(go.Histogram(x=pct, nbinsx=30))
    fig.update_layout(title="Percentage error (±100% clip)", xaxis_title="% error", height=360)
    return {
        "id": "REE.P.PCT_ERR_DIST",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {
            "n": int(mask.sum()),
            "mean_pct": float(np.nanmean(pct)) if len(pct) else None,
        },
    }


def plot_metric_folds_ree(fold_metrics: dict[str, list[float]]) -> dict[str, Any]:
    """REE.P.METRIC_FOLDS — box/strip of each metric across folds."""
    import plotly.graph_objects as go

    fig = go.Figure()
    for name, vals in fold_metrics.items():
        v = [float(x) for x in vals if np.isfinite(x)]
        fig.add_trace(go.Box(y=v, name=name, boxpoints="all", jitter=0.3))
    fig.update_layout(title="Regression metric by fold", yaxis_title="score", height=400)
    return {"id": "REE.P.METRIC_FOLDS", "kind": "plot", "plotly": fig.to_plotly_json()}


def plot_calibration_bins(
    y_true: np.ndarray, y_pred: np.ndarray, *, n_bins: int = 10
) -> dict[str, Any]:
    """REE.P.CALIBRATION_BINS — mean y vs mean ŷ by decile with y=x."""
    import plotly.graph_objects as go

    yt = np.asarray(y_true, dtype=float)
    yp = np.asarray(y_pred, dtype=float)
    order = np.argsort(yp)
    yt, yp = yt[order], yp[order]
    edges = np.array_split(np.arange(len(yp)), n_bins)
    mean_pred, mean_true = [], []
    for idx in edges:
        if len(idx) == 0:
            continue
        mean_pred.append(float(np.nanmean(yp[idx])))
        mean_true.append(float(np.nanmean(yt[idx])))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=mean_pred, y=mean_true, mode="markers+lines", name="bins"))
    lo = min(mean_pred + mean_true) if mean_pred else 0.0
    hi = max(mean_pred + mean_true) if mean_pred else 1.0
    fig.add_trace(
        go.Scatter(x=[lo, hi], y=[lo, hi], mode="lines", name="y=x", line={"dash": "dash"})
    )
    fig.update_layout(
        title="Regression calibration (deciles)",
        xaxis_title="mean ŷ",
        yaxis_title="mean y",
        height=360,
    )
    return {
        "id": "REE.P.CALIBRATION_BINS",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {"mean_pred": mean_pred, "mean_true": mean_true},
    }


def plot_err_segment(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    *,
    n_bins: int = 10,
) -> dict[str, Any]:
    """REE.P.ERR_SEGMENT — MAE and bias by ŷ-decile via fairlearn MetricFrame."""
    import plotly.graph_objects as go
    from fairlearn.metrics import MetricFrame
    from sklearn.metrics import mean_absolute_error

    yt = np.asarray(y_true, dtype=float)
    yp = np.asarray(y_pred, dtype=float)
    try:
        edges = np.quantile(yp, np.linspace(0, 1, n_bins + 1))
        edges = np.unique(edges)
        if len(edges) < 3:
            raise ValueError("too few unique bins")
        labels = np.digitize(yp, edges[1:-1], right=True)
    except Exception:
        labels = np.zeros(len(yp), dtype=int)

    def _bias(y_t: np.ndarray, y_p: np.ndarray) -> float:
        return float(np.nanmean(np.asarray(y_p, dtype=float) - np.asarray(y_t, dtype=float)))

    mf = MetricFrame(
        metrics={"mae": mean_absolute_error, "bias": _bias},
        y_true=yt,
        y_pred=yp,
        sensitive_features=labels,
    )
    by = mf.by_group
    xs = [str(i) for i in by.index.tolist()]
    fig = go.Figure()
    fig.add_trace(go.Bar(name="MAE", x=xs, y=by["mae"].tolist()))
    fig.add_trace(go.Bar(name="bias", x=xs, y=by["bias"].tolist()))
    overall_mae = float(mf.overall["mae"])
    fig.add_hline(y=overall_mae, line_dash="dash", annotation_text="overall MAE")
    fig.update_layout(
        barmode="group",
        title="Error by ŷ decile",
        xaxis_title="ŷ bin",
        yaxis_title="value",
        height=360,
    )
    return {
        "id": "REE.P.ERR_SEGMENT",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {
            "overall_mae": overall_mae,
            "by_group": {
                str(k): {"mae": float(v["mae"]), "bias": float(v["bias"])} for k, v in by.iterrows()
            },
        },
    }


def plot_err_heatmap(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    x: np.ndarray,
    z: np.ndarray,
    *,
    bins: int = 8,
) -> dict[str, Any]:
    """REE.P.ERR_HEATMAP — mean |e| over a 2-feature grid (scipy binned_statistic_2d)."""
    import plotly.graph_objects as go
    from scipy.stats import binned_statistic_2d

    abs_e = np.abs(np.asarray(y_true, dtype=float) - np.asarray(y_pred, dtype=float))
    stat, x_e, y_e, _ = binned_statistic_2d(
        np.asarray(x, dtype=float),
        np.asarray(z, dtype=float),
        abs_e,
        statistic="mean",
        bins=bins,
    )
    fig = go.Figure(
        data=go.Heatmap(
            z=stat.T,
            x=[f"{a:.2f}" for a in 0.5 * (x_e[:-1] + x_e[1:])],
            y=[f"{a:.2f}" for a in 0.5 * (y_e[:-1] + y_e[1:])],
            colorscale="YlOrRd",
        )
    )
    fig.update_layout(title="Mean |error| grid", height=400)
    return {
        "id": "REE.P.ERR_HEATMAP",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {"stat": np.where(np.isnan(stat), None, stat).tolist()},
    }


def plot_compare_bars_ree(
    model_scores: dict[str, float],
    *,
    cis: dict[str, tuple[float, float]] | None = None,
    metric: str = "rmse",
) -> dict[str, Any]:
    """REE.P.COMPARE_BARS — model comparison bars with optional 95% CI."""
    import plotly.graph_objects as go

    names = list(model_scores.keys())
    vals = [float(model_scores[n]) for n in names]
    err = None
    if cis:
        err = [
            [float(model_scores[n] - cis[n][0]) if n in cis else 0.0 for n in names],
            [float(cis[n][1] - model_scores[n]) if n in cis else 0.0 for n in names],
        ]
    fig = go.Figure(
        go.Bar(
            x=names,
            y=vals,
            error_y=(
                {"type": "data", "symmetric": False, "array": err[1], "arrayminus": err[0]}
                if err
                else None
            ),
        )
    )
    fig.update_layout(
        title=f"Regression model comparison ({metric})", yaxis_title=metric, height=360
    )
    return {
        "id": "REE.P.COMPARE_BARS",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {"scores": model_scores, "cis": cis},
    }
