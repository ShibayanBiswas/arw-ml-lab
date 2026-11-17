"""Financial suitability plots — FS.P.* (ARCHITECTURE §37.8)."""

from __future__ import annotations

from typing import Any, Literal

import pandas as pd

from labcore.suitability.fs_checks import (
    _detect_price_col,
    compute_fixed_horizon_label_balance,
    compute_trial_tb_label_balance,
)

LabelMethod = Literal["triple_barrier", "fixed_horizon"]


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