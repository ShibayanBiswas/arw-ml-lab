"""Clustering — sklearn / hdbscan thin wrappers (ARCHITECTURE §18)."""

from __future__ import annotations

from typing import Any, Literal

import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.metrics import (
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)
from sklearn.preprocessing import StandardScaler

ClusterAlgo = Literal["kmeans", "agglomerative", "hdbscan"]


def fit_clustering(
    X: pd.DataFrame | np.ndarray,
    *,
    algorithm: ClusterAlgo = "kmeans",
    n_clusters: int = 3,
    seed: int = 42,
) -> dict[str, Any]:
    """Fit a clustering model; return labels + internal metrics (no fabricated scores)."""
    X_arr = np.asarray(X, dtype=float)
    if X_arr.ndim != 2:
        raise ValueError("X must be 2-d")
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X_arr)

    if algorithm == "kmeans":
        model = KMeans(n_clusters=n_clusters, random_state=seed, n_init=10)
        labels = model.fit_predict(Xs)
        extra = {"inertia": float(model.inertia_), "n_clusters": int(n_clusters)}
    elif algorithm == "agglomerative":
        model = AgglomerativeClustering(n_clusters=n_clusters)
        labels = model.fit_predict(Xs)
        extra = {"n_clusters": int(n_clusters)}
    elif algorithm == "hdbscan":
        import hdbscan  # type: ignore[import-not-found]

        model = hdbscan.HDBSCAN(min_cluster_size=max(5, n_clusters))
        labels = model.fit_predict(Xs)
        n_found = int(len(set(labels)) - (1 if -1 in labels else 0))
        extra = {"n_clusters": n_found, "n_noise": int(np.sum(labels == -1))}
    else:
        raise ValueError(f"unknown clustering algorithm: {algorithm}")

    metrics: dict[str, float | None] = {
        "silhouette": None,
        "calinski_harabasz": None,
        "davies_bouldin": None,
    }
    unique = set(labels.tolist())
    if len(unique) >= 2 and not (len(unique) == 2 and -1 in unique):
        # silhouette needs ≥2 clusters with non-noise points
        mask = labels >= 0 if -1 in unique else np.ones(len(labels), dtype=bool)
        if mask.sum() > 1 and len(set(labels[mask].tolist())) >= 2:
            metrics["silhouette"] = float(silhouette_score(Xs[mask], labels[mask]))
            metrics["calinski_harabasz"] = float(calinski_harabasz_score(Xs[mask], labels[mask]))
            metrics["davies_bouldin"] = float(davies_bouldin_score(Xs[mask], labels[mask]))

    return {
        "id": f"UNSUP.CLUSTER.{algorithm}",
        "algorithm": algorithm,
        "labels": labels.tolist(),
        "metrics": metrics,
        "seed": seed,
        **extra,
    }
