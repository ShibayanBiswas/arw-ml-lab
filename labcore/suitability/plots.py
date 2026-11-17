"""Financial suitability plots — FS.P.* (ARCHITECTURE §37.8)."""

from __future__ import annotations

from typing import Any, Literal

import numpy as np
import pandas as pd

from labcore.suitability.fs_checks import (
    CUSUM_H_GRID,
    PT_SL_GRID,
    VERTICAL_BARRIER_GRID,
    _detect_price_col,
    compute_cusum_filter_events,
    compute_daily_ewma_vol,
    compute_fixed_horizon_label_balance,
    compute_suitability_parameter_grid,
    compute_trial_holding_profile,
    compute_trial_tb_label_balance,
    compute_trial_uniqueness_profile,
    sample_trial_tb_events,
)

LabelMethod = Literal["triple_barrier", "fixed_horizon"]


def _time_axis(df: pd.DataFrame, time_col: str | None) -> list[str]:
    if time_col and time_col in df.columns:
        parsed = pd.to_datetime(df[time_col], errors="coerce")
        return [ts.isoformat() if pd.notna(ts) else "" for ts in parsed]
    if isinstance(df.index, pd.DatetimeIndex):
        return [ts.isoformat() for ts in df.index]
    return [str(i) for i in range(len(df))]


def plot_price_cusum(
    df: pd.DataFrame,
    *,
    price_col: str | None = None,
    time_col: str | None = None,
    vol_span: int = 100,
    cusum_mult: float = 1.0,
    seed: int = 42,
) -> dict[str, Any]:
    """FS.P.PRICE — close series with CUSUM filter event markers (h = cusum_mult × σ̄)."""
    _ = seed
    import plotly.graph_objects as go

    col = price_col or _detect_price_col(df)
    if col is None:
        raise ValueError("no price column detected for CUSUM price plot")
    comp = compute_cusum_filter_events(
        df, col, vol_span=vol_span, h_mult=cusum_mult
    )
    if not comp.get("ok"):
        raise ValueError(comp.get("reason", "CUSUM computation failed"))
    times = _time_axis(df, time_col)
    px = pd.to_numeric(df[col], errors="coerce")
    y = [None if pd.isna(v) else float(v) for v in px.to_numpy()]
    fig = go.Figure(
        data=[
            go.Scatter(
                x=times,
                y=y,
                mode="lines",
                name="close",
                line=dict(color="#1f2937"),
                hovertemplate="t=%{x}<br>price=%{y:.2f}<extra></extra>",
            )
        ]
    )
    up = [ev for ev in comp["events"] if ev["direction"] == 1]
    down = [ev for ev in comp["events"] if ev["direction"] == -1]

    def event_trace(rows: list[dict[str, Any]], name: str, colour: str, symbol: str) -> go.Scatter:
        xs = [times[ev["df_iloc"]] if ev["df_iloc"] < len(times) else str(ev["bar"]) for ev in rows]
        ys = [float(ev["price"]) for ev in rows]
        return go.Scatter(
            x=xs,
            y=ys,
            mode="markers",
            name=name,
            marker=dict(size=9, color=colour, symbol=symbol, line=dict(width=1, color="#fff")),
            hovertemplate=f"{name}<br>t=%{{x}}<br>price=%{{y:.2f}}<extra></extra>",
        )

    if up:
        fig.add_trace(event_trace(up, "CUSUM +", "#2ca02c", "triangle-up"))
    if down:
        fig.add_trace(event_trace(down, "CUSUM −", "#c44e52", "triangle-down"))
    fig.update_layout(
        title=f"Price with CUSUM events (h = {cusum_mult}×σ̄, σ̄ EWMA span={vol_span})",
        xaxis_title="time",
        yaxis_title="price",
        height=460,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    return {
        "id": "FS.P.PRICE",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {
            "price_col": col,
            "time_col": time_col,
            "vol_span": vol_span,
            "cusum_mult": cusum_mult,
            "h": float(comp["h"]),
            "seed": seed,
            "n_events": int(comp["n_events"]),
            "n_up": len(up),
            "n_down": len(down),
            "n_bars": int(len(df)),
        },
    }


def plot_daily_volatility(
    df: pd.DataFrame,
    *,
    price_col: str | None = None,
    time_col: str | None = None,
    span: int = 100,
    seed: int = 42,
) -> dict[str, Any]:
    """FS.P.VOL — EWMA daily volatility series (AFML get_daily_vol equivalent)."""
    _ = seed  # metadata only; vol path is deterministic given prices
    import plotly.graph_objects as go

    comp = compute_daily_ewma_vol(df, price_col, span=span)
    if not comp.get("ok"):
        raise ValueError(comp.get("reason", "daily vol computation failed"))
    col = str(comp["price_col"])
    vol = comp["volatility"]
    x = _time_axis(df, time_col)
    y = [None if pd.isna(v) else float(v) for v in vol.to_numpy()]
    median_vol = comp.get("median_vol")

    fig = go.Figure(
        data=[
            go.Scatter(
                x=x,
                y=y,
                mode="lines",
                name=f"EWMA σ (span={span})",
                hovertemplate="t=%{x}<br>σ=%{y:.4%}<extra></extra>",
            )
        ]
    )
    if median_vol is not None and np.isfinite(median_vol):
        fig.add_hline(
            y=float(median_vol),
            line_dash="dash",
            line_color="#c9a227",
            annotation_text=f"median σ = {median_vol:.3%}",
            annotation_position="right",
        )
    fig.update_layout(
        title="EWMA daily volatility (close-to-close)",
        xaxis_title="time",
        yaxis_title="σ (daily return)",
        height=420,
    )
    return {
        "id": "FS.P.VOL",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {
            "price_col": col,
            "time_col": time_col,
            "span": span,
            "seed": seed,
            "median_vol": None if median_vol is None else float(median_vol),
            "non_null_share": float(comp["non_null_share"]),
            "positive_share": float(comp["positive_share"]),
            "n_bars": int(len(df)),
        },
    }


def plot_label_balance(
    df: pd.DataFrame,
    *,
    price_col: str | None = None,
    method: LabelMethod = "triple_barrier",
    horizon: int = 5,
) -> dict[str, Any]:
    """FS.P.LABEL_BALANCE — bar chart of trial label shares (−1 / 0 / +1)."""
    import plotly.graph_objects as go

    col = price_col or _detect_price_col(df)
    if col is None:
        raise ValueError("no price column detected for label balance plot")
    if method == "triple_barrier":
        bal = compute_trial_tb_label_balance(df, col, horizon=horizon)
    else:
        bal = compute_fixed_horizon_label_balance(df, col, horizon=horizon)
    if not bal.get("ok"):
        raise ValueError(bal.get("reason", "label balance computation failed"))

    xlab = ["−1 (down)", "0 (vertical)", "+1 (up)"]
    keys = [-1, 0, 1]
    shares = [float(bal["shares"][k]) for k in keys]
    counts = [int(bal["counts"][k]) for k in keys]

    fig = go.Figure(
        data=[
            go.Bar(
                x=xlab,
                y=shares,
                text=[f"{s:.1%}" for s in shares],
                textposition="outside",
                customdata=counts,
                hovertemplate="label=%{x}<br>share=%{y:.3%}<br>count=%{customdata}<extra></extra>",
            )
        ]
    )
    fig.add_hline(
        y=0.15,
        line_dash="dash",
        line_color="#c9a227",
        annotation_text="15% minority (PASS)",
        annotation_position="right",
    )
    fig.add_hline(
        y=0.05,
        line_dash="dot",
        line_color="#888",
        annotation_text="5% minority (WARN floor)",
        annotation_position="right",
    )
    title = (
        "Trial triple-barrier label balance"
        if method == "triple_barrier"
        else "Fixed-horizon label balance"
    )
    fig.update_layout(
        title=title,
        yaxis_title="share of events",
        yaxis=dict(range=[0, max(0.55, max(shares) * 1.15)]),
        height=380,
    )
    minority = bal.get("minority_signed_share")
    return {
        "id": "FS.P.LABEL_BALANCE",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {
            "method": method,
            "horizon": horizon,
            "price_col": col,
            "counts": {str(k): counts[i] for i, k in enumerate(keys)},
            "shares": {str(k): shares[i] for i, k in enumerate(keys)},
            "minority_signed_share": None if minority is None else float(minority),
            "vertical_barrier_share": float(bal["vertical_barrier_share"]),
            "n_labels": int(bal["n_labels"]),
        },
    }


def _pt_sl_label(pt_sl: tuple[int, int] | list[int]) -> str:
    return f"{pt_sl[0]}/{pt_sl[1]}"


def plot_suitability_grid(
    df: pd.DataFrame,
    *,
    price_col: str | None = None,
    seed: int = 42,
) -> dict[str, Any]:
    """FS.P.GRID — heatmaps of minority share and n_eff over §37.6 parameter grid."""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    grid = compute_suitability_parameter_grid(df, price_col=price_col, seed=seed)
    col = grid["price_col"]
    vertical_labels = [str(v) for v in VERTICAL_BARRIER_GRID]
    pt_labels = [_pt_sl_label(p) for p in PT_SL_GRID]

    def build_matrix(cusum_mult: float, key: str) -> list[list[float | None]]:
        z: list[list[float | None]] = []
        for pt_sl in PT_SL_GRID:
            row: list[float | None] = []
            for vertical in VERTICAL_BARRIER_GRID:
                match = next(
                    (
                        c
                        for c in grid["cells"]
                        if c["pt_sl"] == list(pt_sl)
                        and c["vertical"] == vertical
                        and c["cusum_mult"] == cusum_mult
                    ),
                    None,
                )
                row.append(None if match is None else match.get(key))
            z.append(row)
        return z

    fig = make_subplots(
        rows=2,
        cols=3,
        subplot_titles=[
            f"CUSUM h = {m}×σ̄ — minority share"
            for m in CUSUM_H_GRID
        ]
        + [f"CUSUM h = {m}×σ̄ — n_eff" for m in CUSUM_H_GRID],
        horizontal_spacing=0.08,
        vertical_spacing=0.12,
    )
    zmax_minority = 0.0
    zmax_neff = 0.0
    for c_idx, cusum_mult in enumerate(CUSUM_H_GRID):
        z_min = build_matrix(cusum_mult, "minority_share")
        z_ne = build_matrix(cusum_mult, "n_eff")
        for v in z_min:
            for x in v:
                if x is not None:
                    zmax_minority = max(zmax_minority, float(x))
        for v in z_ne:
            for x in v:
                if x is not None:
                    zmax_neff = max(zmax_neff, float(x))
        fig.add_trace(
            go.Heatmap(
                z=z_min,
                x=vertical_labels,
                y=pt_labels,
                zmin=0,
                zmax=max(zmax_minority, 0.01),
                colorscale="Viridis",
                colorbar=dict(title="minority", len=0.45, y=0.78)
                if c_idx == 2
                else None,
                showscale=c_idx == 2,
                hovertemplate="pt/sl=%{y}<br>vertical=%{x}<br>minority=%{z:.1%}<extra></extra>",
            ),
            row=1,
            col=c_idx + 1,
        )
        fig.add_trace(
            go.Heatmap(
                z=z_ne,
                x=vertical_labels,
                y=pt_labels,
                zmin=0,
                zmax=max(zmax_neff, 1.0),
                colorscale="Plasma",
                colorbar=dict(title="n_eff", len=0.45, y=0.22)
                if c_idx == 2
                else None,
                showscale=c_idx == 2,
                hovertemplate="pt/sl=%{y}<br>vertical=%{x}<br>n_eff=%{z:.1f}<extra></extra>",
            ),
            row=2,
            col=c_idx + 1,
        )
    fig.update_layout(
        title="Triple-barrier parameter grid (§37.6)",
        height=640,
    )
    for r in (1, 2):
        for c in (1, 2, 3):
            fig.update_xaxes(title_text="vertical (bars)", row=r, col=c)
            fig.update_yaxes(title_text="pt / sl (× σ)", row=r, col=c)

    default = grid.get("default_cell")
    return {
        "id": "FS.P.GRID",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {
            "price_col": col,
            "seed": seed,
            "n_cells": grid["n_cells"],
            "default_cell": default,
            "cells": grid["cells"],
        },
    }


_LABEL_COLOURS = {-1: "#c44e52", 0: "#888888", 1: "#2ca02c"}


def plot_sample_barriers(
    df: pd.DataFrame,
    *,
    price_col: str | None = None,
    time_col: str | None = None,
    horizon: int = 5,
    vol_span: int = 100,
    pt_mult: float = 1.0,
    sl_mult: float = 1.0,
    n_samples: int = 3,
    seed: int = 42,
) -> dict[str, Any]:
    """FS.P.BARRIERS — sample triple-barrier events with PT / SL / vertical levels."""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    col = price_col or _detect_price_col(df)
    if col is None:
        raise ValueError("no price column detected for barrier plot")
    sample = sample_trial_tb_events(
        df,
        col,
        horizon=horizon,
        vol_span=vol_span,
        pt_mult=pt_mult,
        sl_mult=sl_mult,
        n_samples=n_samples,
        seed=seed,
    )
    if not sample.get("ok"):
        raise ValueError(sample.get("reason", "barrier sampling failed"))
    px = pd.to_numeric(df[col], errors="coerce")
    times = _time_axis(df, time_col)
    sampled = sample["sampled_events"]
    n_rows = len(sampled)
    subtitles = [f"label {ev['label']:+d} @ bar {ev['t0']}" for ev in sampled]
    fig = make_subplots(
        rows=n_rows,
        cols=1,
        shared_xaxes=False,
        vertical_spacing=0.06,
        subplot_titles=subtitles,
    )
    numbers_events: list[dict[str, Any]] = []
    for row_idx, ev in enumerate(sampled, start=1):
        t0 = int(ev["t0"])
        t1 = int(ev["t1"])
        vert = int(ev["vertical_t"])
        pad = 2
        i0 = max(0, t0 - pad)
        i1 = min(len(px) - 1, vert + pad)
        xs = times[i0 : i1 + 1]
        ys = [None if pd.isna(px.iloc[j]) else float(px.iloc[j]) for j in range(i0, i1 + 1)]
        fig.add_trace(
            go.Scatter(
                x=xs,
                y=ys,
                mode="lines",
                name="close",
                line=dict(color="#1f2937"),
                showlegend=row_idx == 1,
                hovertemplate="t=%{x}<br>price=%{y:.2f}<extra></extra>",
            ),
            row=row_idx,
            col=1,
        )
        pt_p = float(ev["pt_price"])
        sl_p = float(ev["sl_price"])
        fig.add_hline(
            y=pt_p,
            line_dash="dash",
            line_color="#2ca02c",
            annotation_text="profit-take",
            row=row_idx,
            col=1,
        )
        fig.add_hline(
            y=sl_p,
            line_dash="dash",
            line_color="#c44e52",
            annotation_text="stop-loss",
            row=row_idx,
            col=1,
        )
        if vert <= i1 and vert >= i0:
            fig.add_vline(
                x=times[vert],
                line_dash="dot",
                line_color="#c9a227",
                annotation_text="vertical",
                row=row_idx,
                col=1,
            )
        entry_x = times[t0] if t0 < len(times) else str(t0)
        exit_x = times[t1] if t1 < len(times) else str(t1)
        fig.add_trace(
            go.Scatter(
                x=[entry_x],
                y=[float(ev["entry_price"])],
                mode="markers",
                marker=dict(size=10, color="#c9a227", symbol="circle"),
                name="entry",
                showlegend=row_idx == 1,
                hovertemplate="entry<br>price=%{y:.2f}<extra></extra>",
            ),
            row=row_idx,
            col=1,
        )
        exit_price = ys[t1 - i0] if 0 <= t1 - i0 < len(ys) and ys[t1 - i0] is not None else None
        if exit_price is not None:
            fig.add_trace(
                go.Scatter(
                    x=[exit_x],
                    y=[exit_price],
                    mode="markers",
                    marker=dict(size=10, color=_LABEL_COLOURS[int(ev["label"])], symbol="diamond"),
                    name="exit",
                    showlegend=row_idx == 1,
                    hovertemplate="exit label=%{customdata}<extra></extra>",
                    customdata=[ev["label"]],
                ),
                row=row_idx,
                col=1,
            )
        fig.update_yaxes(title_text="price", row=row_idx, col=1)
        fig.update_xaxes(title_text="time", row=row_idx, col=1)
        numbers_events.append(
            {
                "t0": t0,
                "t1": t1,
                "vertical_t": vert,
                "label": int(ev["label"]),
                "sigma": float(ev["sigma"]),
                "pt_price": pt_p,
                "sl_price": sl_p,
            }
        )
    fig.update_layout(
        title=(
            f"Sample triple-barrier events (pt={pt_mult}×σ, sl={sl_mult}×σ, "
            f"vertical={horizon} bars)"
        ),
        height=max(260, 220 * n_rows),
    )
    return {
        "id": "FS.P.BARRIERS",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {
            "price_col": col,
            "horizon": horizon,
            "vol_span": vol_span,
            "pt_mult": pt_mult,
            "sl_mult": sl_mult,
            "seed": seed,
            "n_events_total": int(sample["n_labels"]),
            "n_panels": n_rows,
            "sampled_events": numbers_events,
        },
    }


def plot_holding_period_distribution(
    df: pd.DataFrame,
    *,
    price_col: str | None = None,
    horizon: int = 5,
    vol_span: int = 100,
    pt_mult: float = 1.0,
    sl_mult: float = 1.0,
    cusum_mult: float | None = None,
    seed: int = 42,
) -> dict[str, Any]:
    """FS.P.HOLDING — histogram of triple-barrier holding periods (bars)."""
    import plotly.graph_objects as go

    col = price_col or _detect_price_col(df)
    if col is None:
        raise ValueError("no price column detected for holding-period plot")
    prof = compute_trial_holding_profile(
        df,
        col,
        horizon=horizon,
        vol_span=vol_span,
        pt_mult=pt_mult,
        sl_mult=sl_mult,
        cusum_mult=cusum_mult,
    )
    if not prof.get("ok"):
        raise ValueError(prof.get("reason", "holding-period profile failed"))

    colours = {"-1": "#c44e52", "0": "#6b7280", "1": "#2ca02c"}
    labels = {"-1": "−1 (down)", "0": "0 (vertical)", "1": "+1 (up)"}
    fig = go.Figure()
    holdings = prof["holding_bars"]
    nbins = min(50, max(8, int(np.sqrt(len(holdings))) + 2))
    for key in ("-1", "0", "1"):
        vals = prof["by_label"][key]
        if not vals:
            continue
        fig.add_trace(
            go.Histogram(
                x=vals,
                name=labels[key],
                nbinsx=nbins,
                marker_color=colours[key],
                opacity=0.72,
                hovertemplate="holding=%{x} bars<br>count=%{y}<extra></extra>",
            )
        )
    fig.add_vline(
        x=float(prof["mean_holding"]),
        line_dash="dash",
        line_color="#c9a227",
        annotation_text=f"mean={prof['mean_holding']:.2f} bars",
        annotation_position="top right",
    )
    fig.add_vline(
        x=float(prof["median_holding"]),
        line_dash="dot",
        line_color="#1f2937",
        annotation_text=f"median={prof['median_holding']:.0f} bars",
        annotation_position="bottom right",
    )
    fig.update_layout(
        title=(
            f"Trial holding-period distribution (pt={pt_mult}×σ, sl={sl_mult}×σ, "
            f"vertical={horizon} bars)"
        ),
        xaxis_title="holding period (bars)",
        yaxis_title="events",
        barmode="overlay",
        height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    return {
        "id": "FS.P.HOLDING",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {
            "price_col": col,
            "horizon": horizon,
            "vol_span": vol_span,
            "pt_mult": pt_mult,
            "sl_mult": sl_mult,
            "cusum_mult": cusum_mult,
            "seed": seed,
            "n_events": int(prof["n_events"]),
            "mean_holding": float(prof["mean_holding"]),
            "median_holding": float(prof["median_holding"]),
            "min_holding": int(prof["min_holding"]),
            "max_holding": int(prof["max_holding"]),
            "by_label_counts": {k: len(prof["by_label"][k]) for k in ("-1", "0", "1")},
        },
    }


def plot_uniqueness_concurrency(
    df: pd.DataFrame,
    *,
    price_col: str | None = None,
    time_col: str | None = None,
    horizon: int = 5,
    vol_span: int = 100,
    seed: int = 42,
) -> dict[str, Any]:
    """FS.P.UNIQUENESS — histogram of per-event ū and concurrency c_t over time."""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    col = price_col or _detect_price_col(df)
    if col is None:
        raise ValueError("no price column detected for uniqueness plot")
    prof = compute_trial_uniqueness_profile(df, col, horizon=horizon, vol_span=vol_span)
    if not prof.get("ok"):
        raise ValueError(prof.get("reason", "uniqueness profile failed"))

    px_df = df.loc[pd.to_numeric(df[col], errors="coerce").notna()]
    times = _time_axis(px_df, time_col)
    n_conc = len(prof["concurrency"])
    x_conc = times[:n_conc] if len(times) >= n_conc else [str(i) for i in range(n_conc)]

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=False,
        vertical_spacing=0.12,
        subplot_titles=("Per-event uniqueness ū (mean 1/c_t)", "Label concurrency c_t over time"),
        row_heights=[0.42, 0.58],
    )
    per_event = prof["per_event_uniqueness"]
    fig.add_trace(
        go.Histogram(
            x=per_event,
            nbinsx=min(40, max(10, len(per_event) // 25)),
            name="ū",
            hovertemplate="ū=%{x:.4f}<br>count=%{y}<extra></extra>",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=x_conc,
            y=prof["concurrency"],
            mode="lines",
            name="c_t",
            line=dict(width=1),
            hovertemplate="t=%{x}<br>c_t=%{y:.0f}<extra></extra>",
        ),
        row=2,
        col=1,
    )
    fig.add_vline(
        x=float(prof["mean_uniqueness"]),
        line_dash="dash",
        line_color="#c9a227",
        row=1,
        col=1,
        annotation_text=f"mean ū={prof['mean_uniqueness']:.3f}",
        annotation_position="top right",
    )
    fig.update_xaxes(title_text="ū", row=1, col=1)
    fig.update_yaxes(title_text="events", row=1, col=1)
    fig.update_xaxes(title_text="time", row=2, col=1)
    fig.update_yaxes(title_text="concurrent labels", row=2, col=1)
    fig.update_layout(
        title=f"Trial label uniqueness and concurrency (±1σ, vertical={horizon} bars)",
        height=520,
        showlegend=False,
    )
    return {
        "id": "FS.P.UNIQUENESS",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {
            "price_col": col,
            "horizon": horizon,
            "vol_span": vol_span,
            "seed": seed,
            "n_spans": int(prof["n_spans"]),
            "mean_uniqueness": float(prof["mean_uniqueness"]),
            "max_concurrency": float(prof["max_concurrency"]),
            "median_concurrency": float(prof["median_concurrency"]),
        },
    }


def plot_min_ffd(
    df: pd.DataFrame,
    *,
    price_col: str | None = None,
    d_step: float = 0.05,
    seed: int = 42,
) -> dict[str, Any]:
    """FS.P.MIN_FFD — ADF statistic and correlation vs fractional-difference order d."""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    from labcore.finance.ffd import scan_min_ffd

    _ = seed
    col = price_col or _detect_price_col(df)
    if col is None:
        raise ValueError("no price column detected for min-FFD plot")
    px = pd.to_numeric(df[col], errors="coerce").dropna()
    if len(px) < 50:
        raise ValueError("need ≥50 prices for min-FFD scan")
    log_px = np.log(px.clip(lower=1e-12).to_numpy(dtype=float))
    scan = scan_min_ffd(log_px, d_step=d_step)
    ds = [r["d"] for r in scan["rows"]]
    adf_stats = [r["adf_statistic"] for r in scan["rows"]]
    corrs = [r["corr_with_original"] for r in scan["rows"]]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=ds,
            y=adf_stats,
            mode="lines+markers",
            name="ADF statistic",
            hovertemplate="d=%{x:.2f}<br>ADF t=%{y:.3f}<extra></extra>",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=ds,
            y=corrs,
            mode="lines+markers",
            name="corr(log price, FFD)",
            line=dict(dash="dot"),
            hovertemplate="d=%{x:.2f}<br>ρ=%{y:.3f}<extra></extra>",
        ),
        secondary_y=True,
    )
    if scan["d_star"] is not None:
        fig.add_vline(
            x=float(scan["d_star"]),
            line_dash="dash",
            line_color="#c9a227",
            annotation_text=f"d*={scan['d_star']:.2f}",
            annotation_position="top",
        )
    fig.update_xaxes(title_text="fractional order d")
    fig.update_yaxes(title_text="ADF statistic (lower → more stationary)", secondary_y=False)
    fig.update_yaxes(title_text="correlation with log price", secondary_y=True, range=[0, 1.05])
    title = "Minimum fractional d for stationarity (ADF 95%)"
    if scan["d_star"] is not None:
        title += f" — d* = {scan['d_star']:.2f}"
    fig.update_layout(
        title=title,
        height=440,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )

    return {
        "id": "FS.P.MIN_FFD",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {
            "price_col": col,
            "n_obs": int(len(log_px)),
            "d_step": d_step,
            "d_star": scan["d_star"],
            "adf_alpha": scan["adf_alpha"],
            "thresh": scan["thresh"],
            "seed": seed,
            "scan": scan["rows"],
        },
    }