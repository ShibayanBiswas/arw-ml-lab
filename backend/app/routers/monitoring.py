"""Drift monitoring API (ARCHITECTURE §26) — thin Phase 7."""

from __future__ import annotations

from typing import Any

import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from labcore.monitoring import ks_drift_report, psi_drift_report
from pydantic import BaseModel, Field

from backend.app.security import AuthUser, require_write_role

router = APIRouter(tags=["monitoring"])


class DriftBody(BaseModel):
    reference: list[list[float]] = Field(min_length=5)
    current: list[list[float]] = Field(min_length=5)
    feature_names: list[str] | None = None
    alpha: float = 0.01


class PsiDriftBody(BaseModel):
    reference: list[list[float]] = Field(min_length=20)
    current: list[list[float]] = Field(min_length=20)
    feature_names: list[str] | None = None
    bins: int = Field(default=10, ge=3, le=50)
    drift_threshold: float = 0.2


@router.post("/api/v1/monitoring/drift/ks")
def monitoring_ks(
    body: DriftBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    _ = user
    try:
        return ks_drift_report(
            np.asarray(body.reference, dtype=float),
            np.asarray(body.current, dtype=float),
            feature_names=body.feature_names,
            alpha=body.alpha,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/v1/monitoring/drift/psi")
def monitoring_psi(
    body: PsiDriftBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    _ = user
    try:
        return psi_drift_report(
            np.asarray(body.reference, dtype=float),
            np.asarray(body.current, dtype=float),
            feature_names=body.feature_names,
            bins=body.bins,
            drift_threshold=body.drift_threshold,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
