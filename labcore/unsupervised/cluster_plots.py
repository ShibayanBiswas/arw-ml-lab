"""Unsupervised clustering catalogue plots (§36 / 6B thin)."""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


def kmeans_k_sweep(
    X: np.ndarray,
    *,
    k_min: int = 2,
    k_max: int = 8,
    seed: int = 42,
) -> dict[str, Any]:
    """Inertia + silhouette vs k (sklearn KMeans). Returns numbers + Plotly."""
    import plotly.graph_objects as go

    Xs = StandardScaler().fit_transform(np.asarray(X, dtype=float))
    ks = list(range(k_min, k_max + 1))
    inertias: list[float] = []
    silhouettes: list[float | None] = []
    for k in ks:
        km = KMeans(n_clusters=k, random_state=seed, n_init=10).fit(Xs)
        inertias.append(float(km.inertia_))
        if k >= 2 and len(set(km.labels_)) >= 2:
            silhouettes.append(float(silhouette_score(Xs, km.labels_)))
        else:
            silhouettes.append(None)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ks, y=inertias, mode="lines+markers", name="inertia", yaxis="y"))
    fig.add_trace(
        go.Scatter(
            x=ks,
            y=[s if s is not None else None for s in silhouettes],
            mode="lines+markers",
            name="silhouette",
            yaxis="y2",
        )
    )
    fig.update_layout(
        title="KMeans k-sweep",
        xaxis_title="k",
        yaxis_title="Inertia",
        yaxis2={"title": "Silhouette", "overlaying": "y", "side": "right"},
        height=400,
    )
    best_k = None
    finite_sil = [(k, s) for k, s in zip(ks, silhouettes, strict=True) if s is not None]
    if finite_sil:
        best_k = max(finite_sil, key=lambda t: t[1])[0]
    return {
        "id": "CLU.P.K_SWEEP",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {
            "k": ks,
            "inertia": inertias,
            "silhouette": silhouettes,
            "best_k_by_silhouette": best_k,
        },
        "seed": seed,
    }
