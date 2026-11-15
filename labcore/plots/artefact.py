"""Artefact envelope — CURSOR_PROMPT §4.2."""

from __future__ import annotations

import base64
from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from labcore.plots.jsonable import jsonable


class Artefact(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    kind: Literal["plot", "table", "metric"]
    stage: str = "eda"
    title: str
    plotly: dict[str, Any] | None = None
    png_b64: str | None = None
    png_uri: str | None = None
    numbers: dict[str, Any] = Field(default_factory=dict)
    table: dict[str, Any] | None = None
    edu_key: str | None = None
    sampled: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())

    @field_validator("numbers", "table", "plotly", mode="before")
    @classmethod
    def _sanitize(cls, v: Any) -> Any:
        return jsonable(v) if v is not None else v


def make_table_artefact(
    artefact_id: str,
    title: str,
    *,
    columns: list[str],
    rows: list[dict[str, Any]],
    numbers: dict[str, Any] | None = None,
    edu_key: str | None = None,
) -> Artefact:
    return Artefact(
        id=artefact_id,
        kind="table",
        title=title,
        table={"columns": columns, "rows": rows},
        numbers=numbers or {"n_rows": len(rows)},
        edu_key=edu_key or f"table.{artefact_id.lower()}",
    )


def make_plot_artefact(
    artefact_id: str,
    title: str,
    fig: Any,
    *,
    numbers: dict[str, Any] | None = None,
    edu_key: str | None = None,
    sampled: bool = False,
    render_png_flag: bool = True,
) -> Artefact:
    plotly_json = fig.to_plotly_json() if hasattr(fig, "to_plotly_json") else fig
    png_b64 = None
    if render_png_flag:
        png_b64 = render_png(fig)
    return Artefact(
        id=artefact_id,
        kind="plot",
        title=title,
        plotly=plotly_json,
        png_b64=png_b64,
        numbers=numbers or {},
        edu_key=edu_key or f"plot.{artefact_id.lower()}",
        sampled=sampled,
    )


def render_png(fig: Any) -> str | None:
    """Render Plotly figure to base64 PNG via kaleido; None if unavailable."""
    try:
        import plotly.graph_objects as go

        if not isinstance(fig, go.Figure):
            fig = go.Figure(fig)
        buf = fig.to_image(format="png", engine="kaleido")
        return base64.b64encode(buf).decode("ascii")
    except Exception:
        # CI/dev without kaleido binary — still ship plotly+numbers
        return None


def empty_figure(title: str, message: str) -> Any:
    import plotly.graph_objects as go

    fig = go.Figure()
    fig.add_annotation(text=message, xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
    fig.update_layout(title=title, template="plotly_white")
    return fig
