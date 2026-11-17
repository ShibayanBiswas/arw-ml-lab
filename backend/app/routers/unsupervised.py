"""Unsupervised routes — clustering / DR / anomaly (ARCHITECTURE §18)."""

from __future__ import annotations

from typing import Any, Literal

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from labcore.unsupervised import fit_anomaly, fit_clustering, fit_dr
from labcore.unsupervised.cluster_plots import kmeans_k_sweep
from labcore.unsupervised.dr_plots import pca_scree, shepard_diagram
from pydantic import BaseModel, Field

from backend.app.security import AuthUser, require_write_role

router = APIRouter(tags=["unsupervised"])


class UnsupBody(BaseModel):
    rows: list[dict[str, Any]] = Field(min_length=2)
    algorithm: str = "kmeans"
    n_clusters: int = 3
    n_components: int = 2
    contamination: float = 0.05
    seed: int = 42
    k_min: int = 2
    k_max: int = 8


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
        return fit_clustering(X, algorithm=algo, n_clusters=body.n_clusters, seed=body.seed)
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
        return fit_anomaly(X, algorithm=algo, contamination=body.contamination, seed=body.seed)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/v1/unsupervised/clustering/k-sweep")
def unsupervised_k_sweep(
    body: UnsupBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """CLU.P.K_SWEEP — inertia + silhouette vs k (seed 42)."""
    _ = user
    X = _frame(body.rows)
    try:
        return kmeans_k_sweep(
            X.to_numpy(dtype=float),
            k_min=body.k_min,
            k_max=body.k_max,
            seed=body.seed,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/v1/unsupervised/dr/scree")
def unsupervised_scree(
    body: UnsupBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """DR.P.SCREE — PCA eigenvalues + Kaiser line (seed 42)."""
    _ = user
    X = _frame(body.rows)
    try:
        return pca_scree(X.to_numpy(dtype=float), seed=body.seed)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/v1/unsupervised/dr/shepard")
def unsupervised_shepard(
    body: UnsupBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """DR.P.SHEPARD after PCA (default) or requested DR algorithm."""
    _ = user
    X = _frame(body.rows)
    algo: Literal["pca", "svd", "tsne", "umap"] = body.algorithm  # type: ignore[assignment]
    if algo not in {"pca", "svd", "tsne", "umap"}:
        algo = "pca"
    try:
        dr = fit_dr(X, algorithm=algo, n_components=body.n_components, seed=body.seed)
        return {
            **shepard_diagram(
                X.to_numpy(dtype=float),
                dr["embedding"],
                seed=body.seed,
            ),
            "trustworthiness": dr.get("trustworthiness"),
            "dr": {"algorithm": dr["algorithm"], "n_components": dr["n_components"]},
        }
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
