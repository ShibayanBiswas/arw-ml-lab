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
    compute_daily_ewma_vol,
    compute_fixed_horizon_label_balance,
    compute_suitability_parameter_grid,
    compute_trial_tb_label_balance,
)

LabelMethod = Literal["triple_barrier", "fixed_horizon"]


def _time_axis(df: pd.DataFrame, time_col: str | None) -> list[str]:
    if time_col and time_col in df.columns:
        parsed = pd.to_datetime(df[time_col], errors="coerce")
        return [ts.isoformat() if pd.notna(ts) else "" for ts in parsed]
    if isinstance(df.index, pd.DatetimeIndex):
        return [ts.isoformat() for ts in df.index]
    return [str(i) for i in range(len(df))]


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