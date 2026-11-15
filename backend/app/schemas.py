"""Shared API schemas (Phase 0)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class Healthz(BaseModel):
    status: Literal["ok"] = "ok"
    seed: int
    service: str
    ai_enabled: bool


class MeResponse(BaseModel):
    user_id: str
    email: str | None
    role: str
    workspace_id: str | None


class JobCreateResponse(BaseModel):
    job_id: str


class JobStatus(BaseModel):
    job_id: str
    status: Literal["queued", "running", "done", "error", "cancelled"]
    progress: float = 0.0
    step: str | None = None
    result: dict[str, Any] | None = None
    error: str | None = None


class ArtefactEnvelope(BaseModel):
    """CURSOR_PROMPT §4.2 — artefact contract (Phase 0 shape)."""

    model_config = ConfigDict(extra="forbid")

    id: str
    kind: Literal["plot", "table", "metric"]
    stage: str
    title: str
    plotly: dict[str, Any] | None = None
    png_uri: str | None = None
    numbers: dict[str, Any] = Field(default_factory=dict)
    edu_key: str | None = None
    run_id: str | None = None
    dataset_version_id: str | None = None
    created_at: str | None = None
