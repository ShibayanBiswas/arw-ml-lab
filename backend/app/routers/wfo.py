"""Walk-forward plan API (ARCHITECTURE §32) — thin Phase 5A."""

from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from labcore.finance.wfo import plan_wfo_windows
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
