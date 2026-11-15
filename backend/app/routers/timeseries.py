"""Time-series thin routes — Phase 4 (HorizonGuard + backtest + analysis)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from labcore.timeseries.analysis import analyse_series
from labcore.timeseries.backtest import rolling_origin_backtest
from labcore.timeseries.horizon_guard import compute_horizon_guard
from pydantic import BaseModel, Field

from backend.app.dataset_store import DATASET_STORE
from backend.app.security import AuthUser, require_write_role

router = APIRouter(tags=["timeseries"])

ROOT = Path(__file__).resolve().parents[3]
_SAMPLE_Y: dict[str, tuple[Path, str, str, float]] = {
    # sample_key → (path, target_col, freq, m)
    "DS22": (ROOT / "data" / "samples" / "airline_passengers.csv", "Passengers", "MS", 12.0),
    "DS23": (ROOT / "data" / "samples" / "shampoo.csv", "Sales", "MS", 12.0),
}


class HorizonBody(BaseModel):
    n: int | None = None
    freq: str = "MS"
    m: float = 12.0
    w: int = 4
    h_request: int | None = None
    sample_id: str | None = None
    dataset_id: str | None = None
    target: str | None = None


class BacktestBody(BaseModel):
    sample_id: str | None = Field(default="DS22")
    dataset_id: str | None = None
    target: str | None = None
    h: int = 12
    w: int = 4
    m: int = 12
    freq: str = "MS"
    models: list[Literal["seasonal_naive", "sarima_airline"]] = Field(
        default_factory=lambda: ["seasonal_naive", "sarima_airline"]
    )


class AnalysisBody(BaseModel):
    sample_id: str | None = "DS22"
    dataset_id: str | None = None
    target: str | None = None
    m: int = 12


def _load_y(
    *,
    sample_id: str | None,
    dataset_id: str | None,
    target: str | None,
) -> tuple[pd.Series, str, float]:
    if sample_id and sample_id in _SAMPLE_Y:
        path, col, freq, m = _SAMPLE_Y[sample_id]
        df = pd.read_csv(path)
        return df[col].astype(float), freq, m
    if dataset_id:
        ds = DATASET_STORE.get(dataset_id)
        if ds is None or not ds.parquet_path:
            raise HTTPException(status_code=404, detail="dataset not found")
        df = pd.read_parquet(ds.parquet_path)
        col = target or (ds.meta or {}).get("target")
        if not col or col not in df.columns:
            raise HTTPException(status_code=422, detail="target column required")
        return df[col].astype(float), "MS", 12.0
    raise HTTPException(status_code=422, detail="sample_id or dataset_id required")


@router.post("/api/v1/timeseries/horizon")
def ts_horizon(body: HorizonBody, user: AuthUser = Depends(require_write_role)) -> dict[str, Any]:
    _ = user
    n = body.n
    freq = body.freq
    m = body.m
    if body.sample_id or body.dataset_id:
        y, freq_s, m_s = _load_y(
            sample_id=body.sample_id, dataset_id=body.dataset_id, target=body.target
        )
        n = len(y)
        freq = freq_s
        m = m_s
    if n is None:
        raise HTTPException(status_code=422, detail="n or sample_id required")
    out = compute_horizon_guard(n, freq, m=m, w=body.w, h_request=body.h_request)
    if body.h_request is not None and not out.get("request_allowed", True):
        raise HTTPException(status_code=422, detail=out)
    return out


@router.post("/api/v1/timeseries/backtest")
def ts_backtest(body: BacktestBody, user: AuthUser = Depends(require_write_role)) -> dict[str, Any]:
    _ = user
    y, freq, m = _load_y(sample_id=body.sample_id, dataset_id=body.dataset_id, target=body.target)
    freq = body.freq or freq
    m_i = int(body.m or m)
    guard = compute_horizon_guard(len(y), freq, m=float(m_i), w=body.w, h_request=body.h)
    if body.h > guard["h_max"]:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "h_exceeds_h_max",
                "horizon": guard,
                "reject_reasons": guard.get("reject_reasons")
                or [f"h={body.h} > h_max={guard['h_max']}"],
            },
        )
    result = rolling_origin_backtest(
        y,
        h=body.h,
        w=body.w,
        m=m_i,
        freq=freq,
        models=list(body.models),
        seed=42,
    )
    if not result.get("ok") and result.get("error") == "h_exceeds_h_max":
        raise HTTPException(status_code=422, detail=result)
    return result


@router.post("/api/v1/timeseries/analysis")
def ts_analysis(body: AnalysisBody, user: AuthUser = Depends(require_write_role)) -> dict[str, Any]:
    _ = user
    y, _freq, m = _load_y(sample_id=body.sample_id, dataset_id=body.dataset_id, target=body.target)
    return analyse_series(y, m=int(body.m or m))
