"""Unsupervised routes — clustering / DR / anomaly (ARCHITECTURE §18)."""

from __future__ import annotations

from math import inf
from typing import Any, Literal

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from labcore.unsupervised import fit_anomaly, fit_clustering, fit_dr
from labcore.unsupervised.anomaly_plots import anomaly_embedding_scatter, anomaly_ranked_bar
from labcore.unsupervised.cluster_plots import (
    correlation_clustermap,
    dbscan_k_distance,
    hierarchical_dendrogram,
    kmeans_calinski_harabasz,
    kmeans_davies_bouldin,
    kmeans_elbow,
    kmeans_gap_statistic,
    kmeans_k_sweep,
    optics_reachability,
    silhouette_knife,
)
from labcore.unsupervised.dr_plots import (
    pca_biplot,
    pca_correlation_circle,
    pca_cumulative_variance,
    pca_loadings_heatmap,
    pca_scree,
    shepard_diagram,
)
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
    n_refs: int = Field(default=50, ge=1, le=200)
    linkage_method: str = "ward"
    truncate_p: int = Field(default=30, ge=2, le=500)
    dendro_max_rows: int = Field(default=2000, ge=3, le=5000)
    clustermap_max_features: int = Field(default=50, ge=2, le=200)
    top_n: int = Field(default=20, ge=1, le=500)
    pc_x: int = Field(default=1, ge=1, le=32)
    pc_y: int = Field(default=2, ge=1, le=32)
    max_pcs: int = Field(default=0, ge=0, le=32)
    min_samples: int = Field(default=0, ge=0, le=500)
    max_eps: float = Field(default=0.0, ge=0.0)
    cluster_method: str = "xi"
    xi: float = Field(default=0.05, gt=0.0, lt=1.0)


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


@router.post("/api/v1/unsupervised/anomaly/ranked")
def unsupervised_anomaly_ranked(
    body: UnsupBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """ANO.P.RANKED — bar chart of top-N anomaly scores (seed 42)."""
    _ = user
    X = _frame(body.rows)
    algo: Literal["isolation_forest", "lof", "pyod_copod"] = body.algorithm  # type: ignore[assignment]
    try:
        fitted = fit_anomaly(X, algorithm=algo, contamination=body.contamination, seed=body.seed)
        ranked = anomaly_ranked_bar(fitted["scores"], top_n=body.top_n)
        return {
            **ranked,
            "algorithm": fitted["algorithm"],
            "contamination": fitted["contamination"],
            "seed": body.seed,
        }
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/v1/unsupervised/anomaly/embed")
def unsupervised_anomaly_embed(
    body: UnsupBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """ANO.P.EMBED — PCA 2D scatter with flagged anomalies highlighted (seed 42)."""
    _ = user
    X = _frame(body.rows)
    algo: Literal["isolation_forest", "lof", "pyod_copod"] = body.algorithm  # type: ignore[assignment]
    try:
        fitted = fit_anomaly(X, algorithm=algo, contamination=body.contamination, seed=body.seed)
        scores = np.asarray(fitted["scores"], dtype=float)
        flags = np.asarray(fitted["is_outlier"], dtype=int)
        embed = anomaly_embedding_scatter(
            X.to_numpy(dtype=float),
            scores,
            flags,
            seed=body.seed,
        )
        return {
            **embed,
            "algorithm": fitted["algorithm"],
            "contamination": fitted["contamination"],
            "threshold": fitted["threshold"],
        }
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/v1/unsupervised/clustering/silhouette")
def unsupervised_silhouette_knife(
    body: UnsupBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """CLU.P.SILHOUETTE — per-sample silhouette knife plot (seed 42)."""
    _ = user
    X = _frame(body.rows)
    try:
        return silhouette_knife(
            X.to_numpy(dtype=float),
            n_clusters=body.n_clusters,
            seed=body.seed,
        )
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


@router.post("/api/v1/unsupervised/clustering/ch")
def unsupervised_calinski_harabasz(
    body: UnsupBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """CLU.P.CH — Calinski-Harabasz vs k (seed 42)."""
    _ = user
    X = _frame(body.rows)
    try:
        return kmeans_calinski_harabasz(
            X.to_numpy(dtype=float),
            k_min=body.k_min,
            k_max=body.k_max,
            seed=body.seed,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/v1/unsupervised/clustering/db")
def unsupervised_davies_bouldin(
    body: UnsupBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """CLU.P.DB — Davies-Bouldin vs k (seed 42)."""
    _ = user
    X = _frame(body.rows)
    try:
        return kmeans_davies_bouldin(
            X.to_numpy(dtype=float),
            k_min=body.k_min,
            k_max=body.k_max,
            seed=body.seed,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/v1/unsupervised/clustering/gap")
def unsupervised_gap_statistic(
    body: UnsupBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """CLU.P.GAP — Tibshirani gap vs k with 1-SE rule (seed 42)."""
    _ = user
    X = _frame(body.rows)
    try:
        return kmeans_gap_statistic(
            X.to_numpy(dtype=float),
            k_min=body.k_min,
            k_max=body.k_max,
            n_refs=body.n_refs,
            seed=body.seed,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/v1/unsupervised/clustering/dendrogram")
def unsupervised_dendrogram(
    body: UnsupBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """CLU.P.DENDROGRAM — truncated hierarchical dendrogram + cophenetic r (seed 42)."""
    _ = user
    X = _frame(body.rows)
    try:
        return hierarchical_dendrogram(
            X.to_numpy(dtype=float),
            linkage_method=body.linkage_method,
            truncate_p=body.truncate_p,
            max_rows=body.dendro_max_rows,
            seed=body.seed,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/v1/unsupervised/clustering/clustermap")
def unsupervised_clustermap(
    body: UnsupBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """CLU.P.CLUSTERMAP — feature correlation heatmap + dendrograms (seed 42)."""
    _ = user
    df = _frame(body.rows)
    cols = [str(c) for c in df.columns]
    link = body.linkage_method
    if link not in {"average", "complete", "single", "weighted"}:
        link = "average"
    try:
        return correlation_clustermap(
            df.to_numpy(dtype=float),
            feature_names=cols,
            linkage_method=link,
            max_features=body.clustermap_max_features,
            seed=body.seed,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/v1/unsupervised/clustering/reachability")
def unsupervised_optics_reachability(
    body: UnsupBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """CLU.P.REACHABILITY — OPTICS reachability valleys (seed 42 metadata)."""
    _ = user
    X = _frame(body.rows)
    ms = None if body.min_samples < 1 else body.min_samples
    max_eps = inf if body.max_eps <= 0.0 else body.max_eps
    try:
        return optics_reachability(
            X.to_numpy(dtype=float),
            min_samples=ms,
            max_eps=float(max_eps),
            cluster_method=body.cluster_method,
            xi=body.xi,
            seed=body.seed,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/v1/unsupervised/clustering/k-distance")
def unsupervised_dbscan_k_distance(
    body: UnsupBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """CLU.P.K_DISTANCE — sorted k-NN distances with Kneedle eps knee (seed 42 metadata)."""
    _ = user
    X = _frame(body.rows)
    ms = None if body.min_samples < 1 else body.min_samples
    try:
        return dbscan_k_distance(
            X.to_numpy(dtype=float),
            min_samples=ms,
            seed=body.seed,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/v1/unsupervised/clustering/elbow")
def unsupervised_elbow(
    body: UnsupBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """CLU.P.ELBOW — inertia vs k with Kneedle knee (seed 42)."""
    _ = user
    X = _frame(body.rows)
    try:
        return kmeans_elbow(
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


@router.post("/api/v1/unsupervised/dr/biplot")
def unsupervised_biplot(
    body: UnsupBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """DR.P.BIPLOT — PCA scores + loading arrows on PC_x × PC_y (seed 42)."""
    _ = user
    df = _frame(body.rows)
    cols = [str(c) for c in df.columns]
    try:
        return pca_biplot(
            df.to_numpy(dtype=float),
            feature_names=cols,
            pc_x=body.pc_x,
            pc_y=body.pc_y,
            seed=body.seed,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/v1/unsupervised/dr/loadings")
def unsupervised_loadings(
    body: UnsupBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """DR.P.LOADINGS — PCA loadings heatmap (seed 42)."""
    _ = user
    df = _frame(body.rows)
    cols = [str(c) for c in df.columns]
    max_pcs = None if body.max_pcs == 0 else body.max_pcs
    try:
        return pca_loadings_heatmap(
            df.to_numpy(dtype=float),
            feature_names=cols,
            seed=body.seed,
            max_components=max_pcs,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/v1/unsupervised/dr/correlation-circle")
def unsupervised_correlation_circle(
    body: UnsupBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """DR.P.CORR_CIRCLE — variable × PC correlations on PC_x × PC_y (seed 42)."""
    _ = user
    df = _frame(body.rows)
    cols = [str(c) for c in df.columns]
    try:
        return pca_correlation_circle(
            df.to_numpy(dtype=float),
            feature_names=cols,
            pc_x=body.pc_x,
            pc_y=body.pc_y,
            seed=body.seed,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/v1/unsupervised/dr/cumvar")
def unsupervised_cumvar(
    body: UnsupBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """DR.P.CUMVAR — PCA cumulative explained variance (seed 42)."""
    _ = user
    X = _frame(body.rows)
    try:
        return pca_cumulative_variance(X.to_numpy(dtype=float), seed=body.seed)
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
