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


def plot_resid_fitted(
    y_pred: np.ndarray, resid: np.ndarray, *, frac: float = 2.0 / 3.0
) -> dict[str, Any]:
    """REE.P.RESID_FITTED — residuals vs fitted with statsmodels LOWESS."""
    import plotly.graph_objects as go
    from statsmodels.nonparametric.smoothers_lowess import lowess

    y_pred = np.asarray(y_pred, dtype=float)
    resid = np.asarray(resid, dtype=float)
    fig = go.Figure(
        go.Scatter(x=y_pred, y=resid, mode="markers", name="residuals", opacity=0.6)
    )
    fig.add_hline(y=0, line_dash="dash")
    lowess_x: list[float] = []
    lowess_y: list[float] = []
    if len(y_pred) >= 3 and np.any(np.isfinite(y_pred) & np.isfinite(resid)):
        sm = lowess(resid, y_pred, frac=frac, return_sorted=True)
        lowess_x = [float(v) for v in sm[:, 0]]
        lowess_y = [float(v) for v in sm[:, 1]]
        fig.add_trace(
            go.Scatter(
                x=lowess_x,
                y=lowess_y,
                mode="lines",
                name="LOWESS",
                line={"width": 2},
            )
        )
    fig.update_layout(
        title="Residuals vs fitted",
        xaxis_title="Fitted",
        yaxis_title="Residual",
        height=400,
    )
    return {
        "id": "REE.P.RESID_FITTED",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {"frac": frac, "lowess_x": lowess_x, "lowess_y": lowess_y},
    }


def plot_residual_scatter(y_pred: np.ndarray, resid: np.ndarray) -> dict[str, Any]:
    """Alias for :func:`plot_resid_fitted` (legacy call sites)."""
    return plot_resid_fitted(y_pred, resid)


def plot_residual_hist(resid: np.ndarray) -> dict[str, Any]:
    import plotly.graph_objects as go

    fig = go.Figure(go.Histogram(x=resid, nbinsx=30))
    fig.update_layout(title="Residual histogram", xaxis_title="Residual", height=400)
    return {"id": "REE.P.RESID_HIST", "kind": "plot", "plotly": fig.to_plotly_json()}


def plot_qq(resid: np.ndarray, *, alpha: float = 0.05) -> dict[str, Any]:
    """REE.P.QQ — residual normal Q-Q with 95% order-statistic envelope.

    Quantiles from ``statsmodels.graphics.gofplots.ProbPlot``; 95% bounds use
    ``scipy.stats.beta`` on order-statistic ranks (David & Nagaraja, 2003).
    """
    import plotly.graph_objects as go
    from scipy import stats
    from statsmodels.graphics.gofplots import ProbPlot

    resid = np.asarray(resid, dtype=float)
    resid = resid[np.isfinite(resid)]
    if len(resid) < 2:
        fig = go.Figure()
        fig.update_layout(title="Normal Q-Q (insufficient data)", height=400)
        return {
            "id": "REE.P.QQ",
            "kind": "plot",
            "plotly": fig.to_plotly_json(),
            "numbers": {"status": "not computed", "n": int(len(resid))},
        }

    pp = ProbPlot(resid, dist=stats.norm, fit=False)
    theoretical = np.asarray(pp.theoretical_quantiles, dtype=float)
    sample = np.asarray(pp.sample_quantiles, dtype=float)
    n = int(pp.nobs)
    mu = float(np.mean(resid))
    sd = float(np.std(resid, ddof=1)) or 1.0
    ranks = np.arange(1, n + 1, dtype=float)
    lo_p = stats.beta.ppf(alpha / 2, ranks, n - ranks + 1)
    hi_p = stats.beta.ppf(1.0 - alpha / 2, ranks, n - ranks + 1)
    env_lo = mu + sd * stats.norm.ppf(lo_p)
    env_hi = mu + sd * stats.norm.ppf(hi_p)
    ref_y = theoretical * sd + mu

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=theoretical,
            y=env_hi,
            mode="lines",
            line={"width": 0},
            showlegend=False,
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=theoretical,
            y=env_lo,
            mode="lines",
            name="95% envelope",
            fill="tonexty",
            fillcolor="rgba(100, 116, 139, 0.15)",
            line={"width": 0},
        )
    )
    fig.add_trace(go.Scatter(x=theoretical, y=sample, mode="markers", name="sample"))
    fig.add_trace(
        go.Scatter(
            x=theoretical,
            y=ref_y,
            mode="lines",
            name="reference",
            line={"dash": "dash"},
        )
    )
    fig.update_layout(
        title="Normal Q-Q",
        xaxis_title="Theoretical quantiles",
        yaxis_title="Sample quantiles",
        height=400,
    )
    return {
        "id": "REE.P.QQ",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {
            "alpha": alpha,
            "n": n,
            "mu": mu,
            "sd": sd,
            "theoretical_quantiles": theoretical.tolist(),
            "sample_quantiles": sample.tolist(),
            "envelope_lo": env_lo.tolist(),
            "envelope_hi": env_hi.tolist(),
            "reference_y": ref_y.tolist(),
        },
    }


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


def plot_scale_location(
    y_pred: np.ndarray, resid: np.ndarray, *, frac: float = 2.0 / 3.0
) -> dict[str, Any]:
    """REE.P.SCALE_LOCATION — √|standardised residual| vs fitted with LOWESS."""
    import plotly.graph_objects as go
    from statsmodels.nonparametric.smoothers_lowess import lowess

    y_pred = np.asarray(y_pred, dtype=float)
    resid = np.asarray(resid, dtype=float)
    sd = float(np.nanstd(resid, ddof=1)) or 1.0
    stud = resid / sd
    scale = np.sqrt(np.abs(stud))
    fig = go.Figure(
        go.Scatter(x=y_pred, y=scale, mode="markers", name="√|stud. resid|", opacity=0.55)
    )
    lowess_x: list[float] = []
    lowess_y: list[float] = []
    if len(y_pred) >= 3 and np.any(np.isfinite(y_pred) & np.isfinite(scale)):
        sm = lowess(scale, y_pred, frac=frac, return_sorted=True)
        lowess_x = [float(v) for v in sm[:, 0]]
        lowess_y = [float(v) for v in sm[:, 1]]
        fig.add_trace(
            go.Scatter(
                x=lowess_x,
                y=lowess_y,
                mode="lines",
                name="LOWESS",
                line={"width": 2},
            )
        )
    fig.update_layout(
        title="Scale-location",
        xaxis_title="Fitted",
        yaxis_title="√|standardised residual|",
        height=400,
    )
    return {
        "id": "REE.P.SCALE_LOCATION",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {"frac": frac, "residual_sd": sd, "lowess_x": lowess_x, "lowess_y": lowess_y},
    }


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


def plot_regression_cd(
    fold_scores: dict[str, list[float]],
    *,
    higher_is_better: bool = False,
    metric: str = "rmse",
    alpha: float = 0.05,
) -> dict[str, Any]:
    """REE.P.CD — Friedman–Nemenyi critical-difference diagram (≥3 models)."""
    import pandas as pd

    from labcore.eval.cd_diagram import friedman_nemenyi, plot_cd_ranks

    df = pd.DataFrame({k: np.asarray(v, dtype=float) for k, v in fold_scores.items()})
    if df.shape[1] < 3 or df.shape[0] < 2:
        return {
            "id": "REE.P.CD",
            "kind": "plot",
            "plotly": {"data": [], "layout": {"title": "CD diagram needs ≥3 models and ≥2 folds"}},
            "numbers": {"status": "not computed", "reason": "need ≥3 models and ≥2 folds"},
        }
    work = df if higher_is_better else -df
    result = friedman_nemenyi(work, alpha=alpha)
    fig = plot_cd_ranks(result)
    if result.get("status") == "ok":
        fig.setdefault("layout", {})["title"] = f"Critical difference ({metric})"
    return {
        "id": "REE.P.CD",
        "kind": "plot",
        "plotly": fig,
        "numbers": {**result, "metric": metric, "higher_is_better": higher_is_better},
    }


def _holm_adjust_symmetric(pmat: np.ndarray) -> np.ndarray:
    """Holm–Bonferroni adjustment for unique off-diagonal p-values (statsmodels)."""
    from statsmodels.stats.multitest import multipletests

    k = int(pmat.shape[0])
    idx_i, idx_j = np.triu_indices(k, k=1)
    pvals = pmat[idx_i, idx_j]
    _, padj, _, _ = multipletests(pvals, method="holm")
    out = np.ones((k, k), dtype=float)
    for n, (i, j) in enumerate(zip(idx_i, idx_j, strict=True)):
        out[i, j] = float(padj[n])
        out[j, i] = float(padj[n])
    return out


def plot_regression_pvalue_heatmap(
    fold_scores: dict[str, list[float]],
    *,
    higher_is_better: bool = False,
    metric: str = "rmse",
    alpha: float = 0.05,
) -> dict[str, Any]:
    """REE.P.PVALUE_HEATMAP — Nemenyi pairwise p-values with Holm adjustment."""
    import pandas as pd
    import plotly.graph_objects as go
    from scikit_posthocs import posthoc_nemenyi_friedman, sign_array

    df = pd.DataFrame({k: np.asarray(v, dtype=float) for k, v in fold_scores.items()})
    if df.shape[1] < 2 or df.shape[0] < 2:
        return {
            "id": "REE.P.PVALUE_HEATMAP",
            "kind": "plot",
            "plotly": {
                "data": [],
                "layout": {"title": "P-value heatmap needs ≥2 models and ≥2 folds"},
            },
            "numbers": {"status": "not computed", "reason": "need ≥2 models and ≥2 folds"},
        }
    work = df if higher_is_better else -df
    names = list(work.columns)
    raw = np.asarray(posthoc_nemenyi_friedman(work.to_numpy()), dtype=float)
    raw_df = pd.DataFrame(raw, index=names, columns=names)
    holm = _holm_adjust_symmetric(raw_df.to_numpy(dtype=float))
    holm_df = pd.DataFrame(holm, index=names, columns=names)
    sig = sign_array(holm_df, alpha=alpha)
    text = np.where(
        sig == 1,
        np.char.add(np.round(holm, 3).astype(str), "*"),
        np.round(holm, 3).astype(str),
    )
    np.fill_diagonal(text, "—")
    fig = go.Figure(
        go.Heatmap(
            z=holm,
            x=names,
            y=names,
            colorscale="Viridis_r",
            zmin=0.0,
            zmax=1.0,
            text=text,
            texttemplate="%{text}",
            hovertemplate="%{y} vs %{x}<br>Holm p=%{z:.4f}<extra></extra>",
        )
    )
    fig.update_layout(
        title=f"Pairwise p-values ({metric}, Holm)",
        xaxis_title="Model",
        yaxis_title="Model",
        height=max(320, 56 * len(names)),
    )
    return {
        "id": "REE.P.PVALUE_HEATMAP",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {
            "status": "ok",
            "metric": metric,
            "higher_is_better": higher_is_better,
            "alpha": alpha,
            "nemenyi_pvalues": raw_df.to_dict(),
            "holm_pvalues": holm_df.to_dict(),
            "significant_pairs": sign_array(holm_df, alpha=alpha).tolist(),
        },
    }


def plot_regression_validation_curve(
    estimator: Any,
    X: np.ndarray,
    y: np.ndarray,
    *,
    param_name: str,
    param_range: list[Any],
    cv: int = 3,
    seed: int = 42,
    scoring: str = "neg_mean_squared_error",
) -> dict[str, Any]:
    """REE.P.VALIDATION — sklearn ``validation_curve`` → Plotly (tuning diagnostic)."""
    import plotly.graph_objects as go
    from sklearn.model_selection import KFold, validation_curve

    X = np.asarray(X)
    y = np.asarray(y, dtype=float)
    cv_splitter = KFold(n_splits=cv, shuffle=True, random_state=seed)
    train_scores, val_scores = validation_curve(
        estimator,
        X,
        y,
        param_name=param_name,
        param_range=param_range,
        cv=cv_splitter,
        scoring=scoring,
        n_jobs=1,
    )
    train_mean = np.mean(train_scores, axis=1)
    train_std = np.std(train_scores, axis=1, ddof=1)
    val_mean = np.mean(val_scores, axis=1)
    val_std = np.std(val_scores, axis=1, ddof=1)
    x = [str(p) for p in param_range]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x,
            y=train_mean,
            error_y={"array": train_std},
            mode="lines+markers",
            name="train",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x,
            y=val_mean,
            error_y={"array": val_std},
            mode="lines+markers",
            name="cv",
        )
    )
    fig.update_layout(
        title=f"Validation curve ({param_name})",
        xaxis_title=param_name,
        yaxis_title=scoring,
        height=400,
    )
    return {
        "id": "REE.P.VALIDATION",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {
            "param_name": param_name,
            "param_range": x,
            "scoring": scoring,
            "seed": seed,
            "cv": cv,
            "train_mean": train_mean.tolist(),
            "val_mean": val_mean.tolist(),
        },
    }


def plot_regression_learning_curve(
    estimator: Any,
    X: np.ndarray,
    y: np.ndarray,
    *,
    cv: int = 3,
    seed: int = 42,
    scoring: str = "r2",
) -> dict[str, Any]:
    """REE.P.LEARNING — sklearn ``learning_curve`` → Plotly (regression, default R²)."""
    import plotly.graph_objects as go
    from sklearn.model_selection import learning_curve

    train_sizes, train_scores, val_scores = learning_curve(
        estimator,
        X,
        y,
        cv=cv,
        scoring=scoring,
        random_state=seed,
        shuffle=True,
        n_jobs=1,
        train_sizes=np.linspace(0.3, 1.0, 5),
    )
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=train_sizes,
            y=np.mean(train_scores, axis=1),
            error_y={"array": np.std(train_scores, axis=1, ddof=1)},
            mode="lines+markers",
            name="train",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=train_sizes,
            y=np.mean(val_scores, axis=1),
            error_y={"array": np.std(val_scores, axis=1, ddof=1)},
            mode="lines+markers",
            name="cv",
        )
    )
    fig.update_layout(
        title="Learning curve",
        xaxis_title="Train size",
        yaxis_title=scoring,
        height=400,
    )
    return {
        "id": "REE.P.LEARNING",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {
            "scoring": scoring,
            "train_sizes": train_sizes.tolist(),
            "train_mean": np.mean(train_scores, axis=1).tolist(),
            "val_mean": np.mean(val_scores, axis=1).tolist(),
        },
    }
