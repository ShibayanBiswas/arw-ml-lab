"""Report builder API (ARCHITECTURE §25) — thin Phase 7."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from labcore.reports import build_reproduction_notebook, build_run_report, notebook_to_json
from pydantic import BaseModel, Field

from backend.app.security import AuthUser, require_write_role

router = APIRouter(tags=["reports"])


class ReportBody(BaseModel):
    title: str = "Run report"
    stage: str = "supervised"
    facts: dict[str, Any] = Field(default_factory=dict)
    insights: dict[str, Any] | None = None


class NotebookBody(BaseModel):
    title: str = "Reproduction"
    dataset_id: str
    algorithm_key: str
    facts: dict[str, Any] = Field(default_factory=dict)
    pip_pins: list[str] | None = None


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


@router.post("/api/v1/reports/notebook")
def reports_notebook(
    body: NotebookBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    _ = user
    nb = build_reproduction_notebook(
        title=body.title,
        dataset_id=body.dataset_id,
        algorithm_key=body.algorithm_key,
        seed=42,
        facts=body.facts,
        pip_pins=body.pip_pins,
    )
    return {
        "id": "REP.T.NOTEBOOK",
        "nbformat_json": notebook_to_json(nb),
        "seed": 42,
    }
