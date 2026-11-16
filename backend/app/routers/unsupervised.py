"""Unsupervised routes — clustering / DR / anomaly (ARCHITECTURE §18)."""

from __future__ import annotations

from typing import Any, Literal

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.app.security import AuthUser, require_write_role
from labcore.unsupervised import fit_anomaly, fit_clustering, fit_dr

router = APIRouter(tags=["unsupervised"])


class UnsupBody(BaseModel):
    rows: list[dict[str, Any]] = Field(min_length=2)
    algorithm: str = "kmeans"
    n_clusters: int = 3
    n_components: int = 2
    contamination: float = 0.05
    seed: int = 42


def _frame(rows: list[dict[str, Any]]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    numeric = df.select_dtypes(include="number")
    if numeric.shape[1] < 1:
        raise HTTPException(status_code=422, detail="need at least one numeric column")
    return numeric.dropna()


@router.post("/api/v1/unsupervised/clustering")
def unsupervised_clustering(
    body: UnsupBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    _ = user
    X = _frame(body.rows)
    algo: Literal["kmeans", "agglomerative", "hdbscan"] = body.algorithm  # type: ignore[assignment]
    try:
        return fit_clustering(
            X, algorithm=algo, n_clusters=body.n_clusters, seed=body.seed
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/v1/unsupervised/dr")
def unsupervised_dr(
    body: UnsupBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    _ = user
    X = _frame(body.rows)
    algo: Literal["pca", "svd", "tsne", "umap"] = body.algorithm  # type: ignore[assignment]
    try:
        return fit_dr(X, algorithm=algo, n_components=body.n_components, seed=body.seed)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/v1/unsupervised/anomaly")
def unsupervised_anomaly(
    body: UnsupBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    _ = user
    X = _frame(body.rows)
    algo: Literal["isolation_forest", "lof", "pyod_copod"] = body.algorithm  # type: ignore[assignment]
    try:
        return fit_anomaly(
            X, algorithm=algo, contamination=body.contamination, seed=body.seed
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
