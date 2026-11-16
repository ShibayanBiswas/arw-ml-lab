"""Financial labelling suitability — FS1–FS20 (ARCHITECTURE §37)."""

from __future__ import annotations

from typing import Any

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.app.security import AuthUser, require_write_role
from labcore.suitability import run_suitability

router = APIRouter(tags=["suitability"])


class SuitabilityBody(BaseModel):
    rows: list[dict[str, Any]] = Field(default_factory=list)
    time_col: str | None = None
    asset: str | None = None
    sample_id: str | None = None


@router.post("/api/v1/suitability/run")
def suitability_run(
    body: SuitabilityBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    _ = user
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
                raise HTTPException(
                    status_code=404, detail=f"sample '{body.sample_id}' not found"
                )
            df = pd.DataFrame(body.rows)
            time_col = body.time_col
        else:
            df = pd.read_csv(entry[0])
            time_col = body.time_col or entry[1]
    else:
        if len(body.rows) < 3:
            raise HTTPException(status_code=422, detail="need sample_id or ≥3 rows")
        df = pd.DataFrame(body.rows)
        time_col = body.time_col
    try:
        return run_suitability(df, time_col=time_col, asset=body.asset)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc