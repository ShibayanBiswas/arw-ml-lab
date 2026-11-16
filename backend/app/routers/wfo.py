"""Walk-forward plan API (ARCHITECTURE §32) — thin Phase 5A."""

from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from labcore.finance.wfo import plan_wfo_windows, run_wfo_regression
from pydantic import BaseModel, Field

from backend.app.security import AuthUser, require_write_role

router = APIRouter(tags=["wfo"])


class WfoPlanBody(BaseModel):
    n: int = Field(ge=20, le=1_000_000)
    n_windows: int = 5
    l_is: int | None = None
    l_oos: int | None = None
    step: int | None = None
    gap: int = 0
    embargo: int = 0
    mode: Literal["expanding", "rolling"] = "expanding"


class WfoRunBody(BaseModel):
    rows: list[dict[str, Any]] = Field(min_length=40, max_length=50_000)
    feature_cols: list[str] = Field(min_length=1)
    target_col: str
    n_windows: int = 5
    l_is: int | None = None
    l_oos: int | None = None
    step: int | None = None
    gap: int = 0
    embargo: int = 0
    mode: Literal["expanding", "rolling"] = "expanding"


@router.post("/api/v1/wfo/plan")
def wfo_plan(
    body: WfoPlanBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    _ = user
    try:
        return plan_wfo_windows(
            body.n,
            n_windows=body.n_windows,
            l_is=body.l_is,
            l_oos=body.l_oos,
            step=body.step,
            gap=body.gap,
            embargo=body.embargo,
            mode=body.mode,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/v1/wfo/run")
def wfo_run(
    body: WfoRunBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    _ = user
    import pandas as pd

    df = pd.DataFrame(body.rows)
    missing = [c for c in [*body.feature_cols, body.target_col] if c not in df.columns]
    if missing:
        raise HTTPException(status_code=422, detail=f"missing columns: {missing}")
    try:
        return run_wfo_regression(
            df[body.feature_cols],
            df[body.target_col],
            n_windows=body.n_windows,
            l_is=body.l_is,
            l_oos=body.l_oos,
            step=body.step,
            gap=body.gap,
            embargo=body.embargo,
            mode=body.mode,
            seed=42,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
