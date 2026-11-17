"""Unsupervised clustering catalogue plots (§36 / 6B thin)."""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import (
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_samples,
    silhouette_score,
)
from sklearn.preprocessing import StandardScaler


def silhouette_knife(
    X: np.ndarray,
    *,
    n_clusters: int = 3,
    seed: int = 42,
) -> dict[str, Any]:
    """Per-sample silhouettes grouped by cluster with overall mean (knife plot)."""
    import plotly.graph_objects as go

    Xs = StandardScaler().fit_transform(np.asarray(X, dtype=float))
    n_rows = Xs.shape[0]
    if n_rows < n_clusters or n_clusters < 2:
        raise ValueError("need n_clusters ≥ 2 and at least n_clusters rows")
    km = KMeans(n_clusters=n_clusters, random_state=seed, n_init=10).fit(Xs)
    labels = np.asarray(km.labels_, dtype=int)
    sil = silhouette_samples(Xs, labels)
    if len(np.unique(labels)) < 2:
        raise ValueError("KMeans produced a single cluster")
    overall = float(silhouette_score(Xs, labels))

    fig = go.Figure()
    y_cursor = 0
    cluster_means: dict[str, float] = {}
    cluster_sizes: dict[str, int] = {}
    order: list[int] = []
    y_labels: list[int] = []
    sil_ordered: list[float] = []
    cluster_by_y: list[int] = []

    for cluster_id in sorted(int(c) for c in np.unique(labels)):
        idx = np.where(labels == cluster_id)[0]
        sort_idx = idx[np.argsort(sil[idx], kind="stable")]
        mean_c = float(np.mean(sil[idx]))
        cluster_means[str(cluster_id)] = mean_c
        cluster_sizes[str(cluster_id)] = int(len(idx))
        fig.add_trace(
            go.Bar(
                x=sil[sort_idx].tolist(),
                y=[y_cursor + i for i in range(len(sort_idx))],
                orientation="h",
                name=f"cluster {cluster_id}",
                marker_line_width=0,
                hovertemplate="cluster=%{customdata}<br>silhouette=%{x:.3f}<extra></extra>",
                customdata=[cluster_id] * len(sort_idx),
                showlegend=True,
            )
        )
        order.extend(sort_idx.tolist())
        for i, row in enumerate(sort_idx):
            y_labels.append(y_cursor + i)
            sil_ordered.append(float(sil[row]))
            cluster_by_y.append(cluster_id)
        y_cursor += len(sort_idx) + 10

    fig.add_vline(
        x=overall,
        line_dash="dash",
        line_color="#222",
        annotation_text=f"mean={overall:.3f}",
        annotation_position="top",
    )
    fig.update_layout(
        title=f"Silhouette knife (k={n_clusters}, mean={overall:.3f})",
        xaxis_title="Silhouette coefficient",
        yaxis_title="Sample (grouped by cluster)",
        barmode="overlay",
        height=max(360, min(700, 40 * len(order) + 120)),
        yaxis=dict(showticklabels=False),
    )
    return {
        "id": "CLU.P.SILHOUETTE",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {
            "n_clusters": n_clusters,
            "overall_silhouette": overall,
            "cluster_mean_silhouette": cluster_means,
            "cluster_sizes": cluster_sizes,
            "silhouette_by_sample": sil_ordered,
            "cluster_by_sample": cluster_by_y,
            "sample_order": order,
        },
        "seed": seed,
    }


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


def kmeans_elbow(
    X: np.ndarray,
    *,
    k_min: int = 2,
    k_max: int = 10,
    seed: int = 42,
) -> dict[str, Any]:
    """Inertia vs k with Kneedle knee (elbow method). Returns numbers + Plotly."""
    import plotly.graph_objects as go
    from kneed import KneeLocator

    Xs = StandardScaler().fit_transform(np.asarray(X, dtype=float))
    ks = list(range(k_min, k_max + 1))
    inertias: list[float] = []
    for k in ks:
        km = KMeans(n_clusters=k, random_state=seed, n_init=10).fit(Xs)
        inertias.append(float(km.inertia_))

    knee: int | None = None
    knee_y: float | None = None
    if len(ks) >= 3:
        locator = KneeLocator(ks, inertias, curve="convex", direction="decreasing", S=1.0)
        if locator.knee is not None:
            knee = int(locator.knee)
            knee_y = float(locator.knee_y) if locator.knee_y is not None else None

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=ks,
            y=inertias,
            mode="lines+markers",
            name="inertia (WCSS)",
        )
    )
    if knee is not None and knee_y is not None:
        fig.add_vline(
            x=knee,
            line_dash="dash",
            line_color="#c9a227",
            annotation_text=f"elbow k={knee}",
            annotation_position="top",
        )
        fig.add_trace(
            go.Scatter(
                x=[knee],
                y=[knee_y],
                mode="markers",
                name="knee",
                marker={"size": 12, "color": "#c9a227", "symbol": "diamond"},
            )
        )
    title = f"KMeans elbow (knee k={knee})" if knee is not None else "KMeans elbow"
    fig.update_layout(
        title=title,
        xaxis_title="k",
        yaxis_title="Inertia (WCSS)",
        height=400,
    )
    return {
        "id": "CLU.P.ELBOW",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {
            "k": ks,
            "inertia": inertias,
            "knee_k": knee,
            "knee_inertia": knee_y,
        },
        "seed": seed,
    }


def kmeans_calinski_harabasz(
    X: np.ndarray,
    *,
    k_min: int = 2,
    k_max: int = 10,
    seed: int = 42,
) -> dict[str, Any]:
    """Calinski-Harabasz index vs k (higher is better). Returns numbers + Plotly."""
    import plotly.graph_objects as go

    Xs = StandardScaler().fit_transform(np.asarray(X, dtype=float))
    ks = list(range(k_min, k_max + 1))
    ch_scores: list[float | None] = []
    for k in ks:
        km = KMeans(n_clusters=k, random_state=seed, n_init=10).fit(Xs)
        if k >= 2 and len(set(km.labels_)) >= 2:
            ch_scores.append(float(calinski_harabasz_score(Xs, km.labels_)))
        else:
            ch_scores.append(None)

    best_k: int | None = None
    best_ch: float | None = None
    finite = [(k, s) for k, s in zip(ks, ch_scores, strict=True) if s is not None]
    if finite:
        best_k, best_ch = max(finite, key=lambda t: t[1])

    fig = go.Figure()
    y_plot = [s if s is not None else None for s in ch_scores]
    fig.add_trace(
        go.Scatter(
            x=ks,
            y=y_plot,
            mode="lines+markers",
            name="Calinski-Harabasz",
        )
    )
    if best_k is not None and best_ch is not None:
        fig.add_vline(
            x=best_k,
            line_dash="dash",
            line_color="#c9a227",
            annotation_text=f"max CH k={best_k}",
            annotation_position="top",
        )
        fig.add_trace(
            go.Scatter(
                x=[best_k],
                y=[best_ch],
                mode="markers",
                name="best k",
                marker={"size": 12, "color": "#c9a227", "symbol": "diamond"},
            )
        )
    title = (
        f"Calinski-Harabasz vs k (best k={best_k})"
        if best_k is not None
        else "Calinski-Harabasz vs k"
    )
    fig.update_layout(
        title=title,
        xaxis_title="k",
        yaxis_title="Calinski-Harabasz index",
        height=400,
    )
    return {
        "id": "CLU.P.CH",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {
            "k": ks,
            "calinski_harabasz": ch_scores,
            "best_k_by_ch": best_k,
            "best_ch": best_ch,
        },
        "seed": seed,
    }


def kmeans_davies_bouldin(
    X: np.ndarray,
    *,
    k_min: int = 2,
    k_max: int = 10,
    seed: int = 42,
) -> dict[str, Any]:
    """Davies-Bouldin index vs k (lower is better). Returns numbers + Plotly."""
    import plotly.graph_objects as go

    Xs = StandardScaler().fit_transform(np.asarray(X, dtype=float))
    ks = list(range(k_min, k_max + 1))
    db_scores: list[float | None] = []
    for k in ks:
        km = KMeans(n_clusters=k, random_state=seed, n_init=10).fit(Xs)
        if k >= 2 and len(set(km.labels_)) >= 2:
            db_scores.append(float(davies_bouldin_score(Xs, km.labels_)))
        else:
            db_scores.append(None)

    best_k: int | None = None
    best_db: float | None = None
    finite = [(k, s) for k, s in zip(ks, db_scores, strict=True) if s is not None]
    if finite:
        best_k, best_db = min(finite, key=lambda t: t[1])

    fig = go.Figure()
    y_plot = [s if s is not None else None for s in db_scores]
    fig.add_trace(
        go.Scatter(
            x=ks,
            y=y_plot,
            mode="lines+markers",
            name="Davies-Bouldin",
        )
    )
    if best_k is not None and best_db is not None:
        fig.add_vline(
            x=best_k,
            line_dash="dash",
            line_color="#c9a227",
            annotation_text=f"min DB k={best_k}",
            annotation_position="top",
        )
        fig.add_trace(
            go.Scatter(
                x=[best_k],
                y=[best_db],
                mode="markers",
                name="best k",
                marker={"size": 12, "color": "#c9a227", "symbol": "diamond"},
            )
        )
    title = (
        f"Davies-Bouldin vs k (best k={best_k})"
        if best_k is not None
        else "Davies-Bouldin vs k"
    )
    fig.update_layout(
        title=title,
        xaxis_title="k",
        yaxis_title="Davies-Bouldin index",
        height=400,
    )
    return {
        "id": "CLU.P.DB",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {
            "k": ks,
            "davies_bouldin": db_scores,
            "best_k_by_db": best_k,
            "best_db": best_db,
        },
        "seed": seed,
    }


def _kmeans_log_inertia(X: np.ndarray, k: int, seed: int) -> float:
    """log WCSS for Tibshirani gap statistic (sklearn KMeans inertia)."""
    tiny = np.finfo(float).tiny
    km = KMeans(n_clusters=k, random_state=seed, n_init=10).fit(X)
    inertia = max(float(km.inertia_), tiny)
    return float(np.log(inertia))


def kmeans_gap_statistic(
    X: np.ndarray,
    *,
    k_min: int = 2,
    k_max: int = 10,
    n_refs: int = 50,
    seed: int = 42,
) -> dict[str, Any]:
    """Gap statistic vs k with 1-SE rule (Tibshirani et al. 2001; sklearn KMeans WCSS)."""
    import plotly.graph_objects as go

    if n_refs < 1:
        raise ValueError("n_refs must be ≥ 1")
    Xs = StandardScaler().fit_transform(np.asarray(X, dtype=float))
    n_rows = Xs.shape[0]
    if n_rows < k_min or k_max < k_min:
        raise ValueError("need enough rows for k_min and k_max")
    ks = list(range(k_min, k_max + 1))
    rng = np.random.default_rng(seed)
    lows = Xs.min(axis=0)
    highs = Xs.max(axis=0)

    log_wk: list[float] = []
    gap: list[float] = []
    gap_se: list[float] = []
    ref_log_mean: list[float] = []

    for i, k in enumerate(ks):
        log_wk.append(_kmeans_log_inertia(Xs, k, seed))
        ref_logs: list[float] = []
        for b in range(n_refs):
            ref = rng.uniform(lows, highs, size=Xs.shape)
            ref_seed = seed + k * 10_000 + b
            ref_logs.append(_kmeans_log_inertia(ref, k, ref_seed))
        ref_arr = np.asarray(ref_logs, dtype=float)
        mean_ref = float(ref_arr.mean())
        ref_log_mean.append(mean_ref)
        gap_k = mean_ref - log_wk[i]
        gap.append(gap_k)
        std_ref = float(ref_arr.std(ddof=1)) if n_refs > 1 else 0.0
        gap_se.append(std_ref * float(np.sqrt(1.0 + 1.0 / n_refs)))

    best_k: int | None = None
    for i in range(len(ks) - 1):
        if gap[i] >= gap[i + 1] - gap_se[i + 1]:
            best_k = ks[i]
            break
    if best_k is None:
        best_k = ks[-1]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=ks,
            y=gap,
            mode="lines+markers",
            name="Gap(k)",
            error_y={"type": "data", "array": gap_se, "visible": True},
        )
    )
    best_gap = gap[ks.index(best_k)]
    fig.add_vline(
        x=best_k,
        line_dash="dash",
        line_color="#c9a227",
        annotation_text=f"1-SE k={best_k}",
        annotation_position="top",
    )
    fig.add_trace(
        go.Scatter(
            x=[best_k],
            y=[best_gap],
            mode="markers",
            name="1-SE choice",
            marker={"size": 12, "color": "#c9a227", "symbol": "diamond"},
        )
    )
    fig.update_layout(
        title=f"Gap statistic vs k (1-SE k={best_k}, B={n_refs})",
        xaxis_title="k",
        yaxis_title="Gap(k)",
        height=400,
    )
    return {
        "id": "CLU.P.GAP",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {
            "k": ks,
            "log_wk": log_wk,
            "ref_log_wk_mean": ref_log_mean,
            "gap": gap,
            "gap_standard_error": gap_se,
            "n_refs": n_refs,
            "best_k_1se": best_k,
            "best_gap": best_gap,
        },
        "seed": seed,
    }


def hierarchical_dendrogram(
    X: np.ndarray,
    *,
    linkage_method: str = "ward",
    metric: str = "euclidean",
    truncate_p: int = 30,
    max_rows: int = 2000,
    seed: int = 42,
) -> dict[str, Any]:
    """Agglomerative dendrogram (truncated) with cophenetic correlation (scipy)."""
    import plotly.graph_objects as go
    from scipy.cluster import hierarchy
    from scipy.spatial.distance import pdist

    Xs = StandardScaler().fit_transform(np.asarray(X, dtype=float))
    n_rows = Xs.shape[0]
    if n_rows < 2:
        raise ValueError("need at least 2 rows for hierarchical clustering")
    if n_rows > max_rows:
        raise ValueError(f"at most {max_rows} rows for dendrogram (got {n_rows})")
    if linkage_method == "ward" and metric != "euclidean":
        raise ValueError("Ward linkage requires euclidean metric")

    condensed = pdist(Xs, metric=metric)
    z_link = hierarchy.linkage(condensed, method=linkage_method)
    coph_corr, _coph_dists = hierarchy.cophenet(z_link, condensed)
    color_threshold = 0.7 * float(np.max(z_link[:, 2]))
    p_show = min(truncate_p, n_rows - 1)
    ddata = hierarchy.dendrogram(
        z_link,
        truncate_mode="lastp",
        p=p_show,
        color_threshold=color_threshold,
        no_plot=True,
    )

    mpl_tab10 = (
        "#1f77b4",
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",
        "#8c564b",
        "#e377c2",
        "#7f7f7f",
        "#bcbd22",
        "#17becf",
    )

    def _plotly_line_color(mpl_color: str) -> str:
        if mpl_color.startswith("C") and mpl_color[1:].isdigit():
            return mpl_tab10[int(mpl_color[1:]) % len(mpl_tab10)]
        if mpl_color in {"k", "black"}:
            return "#222222"
        return mpl_color if mpl_color.startswith("#") else "#636363"

    fig = go.Figure()
    for icoord, dcoord, color in zip(
        ddata["icoord"], ddata["dcoord"], ddata["color_list"], strict=True
    ):
        fig.add_trace(
            go.Scatter(
                x=icoord,
                y=dcoord,
                mode="lines",
                line={"color": _plotly_line_color(color), "width": 1.5},
                showlegend=False,
                hoverinfo="skip",
            )
        )
    title = f"Hierarchical dendrogram ({linkage_method}, cophenetic r={coph_corr:.3f})"
    fig.update_layout(
        title=title,
        xaxis_title="Cluster / leaf",
        yaxis_title="Linkage distance",
        height=480,
        showlegend=False,
    )
    return {
        "id": "CLU.P.DENDROGRAM",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {
            "n_rows": n_rows,
            "linkage_method": linkage_method,
            "metric": metric,
            "truncate_p": p_show,
            "color_threshold": color_threshold,
            "cophenetic_correlation": float(coph_corr),
            "ivl_labels": list(ddata["ivl"]),
            "n_merge_segments": len(ddata["icoord"]),
        },
        "seed": seed,
    }
