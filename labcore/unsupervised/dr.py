"""Dimensionality reduction — sklearn / umap thin wrappers (ARCHITECTURE §18)."""

from __future__ import annotations

from typing import Any, Literal

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler

DrAlgo = Literal["pca", "svd", "tsne", "umap"]


def fit_dr(
    X: pd.DataFrame | np.ndarray,
    *,
    algorithm: DrAlgo = "pca",
    n_components: int = 2,
    seed: int = 42,
) -> dict[str, Any]:
    """Project X; return embedding + explained variance when the library provides it."""
    X_arr = np.asarray(X, dtype=float)
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X_arr)
    n_components = min(n_components, Xs.shape[1], max(1, Xs.shape[0] - 1))

    explained: list[float] | None = None
    if algorithm == "pca":
        model = PCA(n_components=n_components, random_state=seed)
        emb = model.fit_transform(Xs)
        explained = [float(v) for v in model.explained_variance_ratio_]
    elif algorithm == "svd":
        model = TruncatedSVD(n_components=n_components, random_state=seed)
        emb = model.fit_transform(Xs)
        explained = [float(v) for v in model.explained_variance_ratio_]
    elif algorithm == "tsne":
        model = TSNE(
            n_components=min(n_components, 3),
            random_state=seed,
            perplexity=min(30, max(5, Xs.shape[0] // 4)),
        )
        emb = model.fit_transform(Xs)
    elif algorithm == "umap":
        import umap  # type: ignore[import-not-found]

        model = umap.UMAP(n_components=n_components, random_state=seed)
        emb = model.fit_transform(Xs)
    else:
        raise ValueError(f"unknown DR algorithm: {algorithm}")

    return {
        "id": f"UNSUP.DR.{algorithm}",
        "algorithm": algorithm,
        "embedding": np.asarray(emb, dtype=float).tolist(),
        "n_components": int(emb.shape[1]),
        "explained_variance_ratio": explained,
        "seed": seed,
    }
