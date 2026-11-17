"""Report builder API (ARCHITECTURE §25) — thin Phase 7."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from labcore.reports import (
    build_executive_html,
    build_formula_sheet,
    build_reproduction_bundle_zip,
    build_reproduction_notebook,
    build_run_report,
    bundle_to_base64,
    notebook_to_json,
    render_executive_pdf_b64,
)
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
    data_sha256: str | None = None


class FormulasBody(BaseModel):
    title: str = "Metric formula sheet"
    families: list[str] | None = None


@router.post("/api/v1/reports/build")
def reports_build(
    body: ReportBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    _ = user
    report = build_run_report(
        title=body.title,
        stage=body.stage,
        facts=body.facts,
        insights=body.insights,
        seed=42,
    )
    report["id"] = "REP.T.BUILDER"
    return report


@router.post("/api/v1/reports/executive")
def reports_executive(
    body: ReportBody,
    user: AuthUser = Depends(require_write_role),
    include_pdf: bool = False,
) -> dict[str, Any]:
    _ = user
    html_doc = build_executive_html(
        title=body.title,
        stage=body.stage,
        facts=body.facts,
        insights=body.insights,
        seed=42,
    )
    out: dict[str, Any] = {
        "id": "REP.T.EXECUTIVE",
        "seed": 42,
        "html": html_doc,
        "pdf_available": False,
    }
    if include_pdf:
        try:
            out["pdf_base64"] = render_executive_pdf_b64(html_doc)
            out["pdf_available"] = True
        except Exception:  # noqa: BLE001 — Pango missing on dev Windows
            out["pdf_available"] = False
    return out


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


@router.post("/api/v1/reports/bundle")
def reports_bundle(
    body: NotebookBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    _ = user
    blob = build_reproduction_bundle_zip(
        title=body.title,
        dataset_id=body.dataset_id,
        algorithm_key=body.algorithm_key,
        seed=42,
        facts=body.facts,
        pip_pins=body.pip_pins,
        data_hash=body.data_sha256,
    )
    slug = f"{body.dataset_id}-{body.algorithm_key}".replace("/", "_")
    return {
        "id": "REP.T.BUNDLE",
        "seed": 42,
        "timezone": "Asia/Kolkata",
        "filename": f"reproduction-{slug}-seed42.zip",
        "zip_base64": bundle_to_base64(blob),
    }


@router.post("/api/v1/reports/formulas")
def reports_formulas(
    body: FormulasBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    _ = user
    return build_formula_sheet(title=body.title, families=body.families, seed=42)