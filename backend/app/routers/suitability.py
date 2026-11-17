"""Financial labelling suitability — FS1–FS20 (ARCHITECTURE §37)."""

from __future__ import annotations

from typing import Any

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from labcore.suitability import (
    plot_daily_volatility,
    plot_holding_period_distribution,
    plot_min_ffd,
    plot_price_cusum,
    plot_sadf,
    plot_sample_barriers,
    plot_trendscan,
    plot_uniqueness_concurrency,
    run_suitability,
)
from pydantic import BaseModel, Field

from backend.app.security import AuthUser, require_write_role

router = APIRouter(tags=["suitability"])


class SuitabilityBody(BaseModel):
    rows: list[dict[str, Any]] = Field(default_factory=list)
    time_col: str | None = None
    asset: str | None = None
    sample_id: str | None = None
    price_col: str | None = None
    vol_span: int = Field(default=100, ge=10, le=500)
    horizon: int = Field(default=5, ge=1, le=60)
    pt_mult: float = Field(default=1.0, gt=0.0, le=10.0)
    sl_mult: float = Field(default=1.0, gt=0.0, le=10.0)
    n_samples: int = Field(default=3, ge=1, le=6)
    cusum_mult: float = Field(default=1.0, gt=0.0, le=5.0)
    d_step: float = Field(default=0.05, gt=0.01, le=0.25)
    min_window: int = Field(default=30, ge=10, le=120)
    max_lookback: int = Field(default=60, ge=20, le=252)
    sadf_maxlag: int = Field(default=0, ge=0, le=10)
    sadf_end_step: int = Field(default=3, ge=1, le=10)
    trendscan_l_min: int = Field(default=5, ge=3, le=30)
    trendscan_l_max: int = Field(default=20, ge=5, le=60)
    trendscan_step: int = Field(default=1, ge=1, le=10)


def _load_suitability_frame(
    body: SuitabilityBody,
) -> tuple[pd.DataFrame, str | None]:
    if body.sample_id:
        from pathlib import Path

        root = Path(__file__).resolve().parents[3]
        mapping = {
            "DS22": (root / "data" / "samples" / "airline_passengers.csv", "Month"),
            "DS23": (root / "data" / "samples" / "airline_passengers.csv", "Month"),
            "DS30": (root / "data" / "samples" / "nifty50_daily_5y.csv", "date"),
        }
        entry = mapping.get(body.sample_id)
        if entry is None or not entry[0].exists():
            if not body.rows:
                raise HTTPException(status_code=404, detail=f"sample '{body.sample_id}' not found")
            return pd.DataFrame(body.rows), body.time_col
        df = pd.read_csv(entry[0])
        return df, body.time_col or entry[1]
    if len(body.rows) < 3:
        raise HTTPException(status_code=422, detail="need sample_id or ≥3 rows")
    return pd.DataFrame(body.rows), body.time_col


@router.post("/api/v1/suitability/run")
def suitability_run(
    body: SuitabilityBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    _ = user
    df, time_col = _load_suitability_frame(body)
    try:
        return run_suitability(df, time_col=time_col, asset=body.asset)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/v1/suitability/plots/volatility")
def suitability_volatility_plot(
    body: SuitabilityBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """FS.P.VOL — EWMA daily volatility (seed 42)."""
    _ = user
    df, time_col = _load_suitability_frame(body)
    try:
        return plot_daily_volatility(
            df,
            price_col=body.price_col,
            time_col=time_col,
            span=body.vol_span,
            seed=42,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/v1/suitability/plots/price")
def suitability_price_cusum_plot(
    body: SuitabilityBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """FS.P.PRICE — close with CUSUM event markers (seed 42)."""
    _ = user
    df, time_col = _load_suitability_frame(body)
    try:
        return plot_price_cusum(
            df,
            price_col=body.price_col,
            time_col=time_col,
            vol_span=body.vol_span,
            cusum_mult=body.cusum_mult,
            seed=42,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/v1/suitability/plots/barriers")
def suitability_barriers_plot(
    body: SuitabilityBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """FS.P.BARRIERS — sample events with profit-take, stop-loss, vertical barriers (seed 42)."""
    _ = user
    df, time_col = _load_suitability_frame(body)
    try:
        return plot_sample_barriers(
            df,
            price_col=body.price_col,
            time_col=time_col,
            horizon=body.horizon,
            vol_span=body.vol_span,
            pt_mult=body.pt_mult,
            sl_mult=body.sl_mult,
            n_samples=body.n_samples,
            seed=42,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/v1/suitability/plots/uniqueness")
def suitability_uniqueness_plot(
    body: SuitabilityBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """FS.P.UNIQUENESS — per-event ū histogram and concurrency over time (seed 42)."""
    _ = user
    df, time_col = _load_suitability_frame(body)
    try:
        return plot_uniqueness_concurrency(
            df,
            price_col=body.price_col,
            time_col=time_col,
            horizon=body.horizon,
            vol_span=body.vol_span,
            seed=42,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/v1/suitability/plots/holding")
def suitability_holding_plot(
    body: SuitabilityBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """FS.P.HOLDING — triple-barrier holding-period histogram (seed 42)."""
    _ = user
    df, _time_col = _load_suitability_frame(body)
    try:
        return plot_holding_period_distribution(
            df,
            price_col=body.price_col,
            horizon=body.horizon,
            vol_span=body.vol_span,
            pt_mult=body.pt_mult,
            sl_mult=body.sl_mult,
            cusum_mult=None,
            seed=42,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/v1/suitability/plots/min-ffd")
def suitability_min_ffd_plot(
    body: SuitabilityBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """FS.P.MIN_FFD — ADF statistic vs fractional-difference order (seed 42 metadata)."""
    _ = user
    df, _time_col = _load_suitability_frame(body)
    try:
        return plot_min_ffd(df, price_col=body.price_col, d_step=body.d_step, seed=42)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/v1/suitability/plots/sadf")
def suitability_sadf_plot(
    body: SuitabilityBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """FS.P.SADF — supremum ADF statistic over time (seed 42 metadata)."""
    _ = user
    df, time_col = _load_suitability_frame(body)
    if body.max_lookback < body.min_window:
        raise HTTPException(status_code=422, detail="max_lookback must be ≥ min_window")
    try:
        return plot_sadf(
            df,
            price_col=body.price_col,
            time_col=time_col,
            min_window=body.min_window,
            max_lookback=body.max_lookback,
            maxlag=body.sadf_maxlag,
            end_step=body.sadf_end_step,
            seed=42,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/v1/suitability/plots/trendscan")
def suitability_trendscan_plot(
    body: SuitabilityBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """FS.P.TRENDSCAN — trend-scan slope t-stat series (seed 42 metadata)."""
    _ = user
    df, time_col = _load_suitability_frame(body)
    if body.trendscan_l_max < body.trendscan_l_min:
        raise HTTPException(
            status_code=422, detail="trendscan_l_max must be ≥ trendscan_l_min"
        )
    try:
        return plot_trendscan(
            df,
            price_col=body.price_col,
            time_col=time_col,
            l_min=body.trendscan_l_min,
            l_max=body.trendscan_l_max,
            step=body.trendscan_step,
            seed=42,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
