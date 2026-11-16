"""Report builder API (ARCHITECTURE §25) — thin Phase 7."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from labcore.reports import build_run_report
from pydantic import BaseModel, Field

from backend.app.security import AuthUser, require_write_role

router = APIRouter(tags=["reports"])


class ReportBody(BaseModel):
    title: str = "Run report"
    stage: str = "supervised"
    facts: dict[str, Any] = Field(default_factory=dict)
    insights: dict[str, Any] | None = None


@router.post("/api/v1/reports/build")
def reports_build(
    body: ReportBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    _ = user
    return build_run_report(
        title=body.title,
        stage=body.stage,
        facts=body.facts,
        insights=body.insights,
        seed=42,
    )
