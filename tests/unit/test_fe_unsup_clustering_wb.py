"""Clustering workbench exposes CLU.P catalogue actions (oneshot-c131, c138)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WB = ROOT / "frontend" / "src" / "components" / "unsupervised" / "UnsupervisedWorkbench.tsx"
API = ROOT / "frontend" / "src" / "lib" / "api.ts"


def test_clustering_workbench_wires_clu_catalogue() -> None:
    src = WB.read_text(encoding="utf-8")
    assert "runUnsupervisedClusteringPlot" in src
    for artefact in (
        "CLU.P.ELBOW",
        "CLU.P.SILHOUETTE",
        "CLU.P.K_SWEEP",
        "CLU.P.CH",
        "CLU.P.DB",
        "CLU.P.GAP",
        "CLU.P.DENDROGRAM",
        "CLU.P.CLUSTERMAP",
        "CLU.P.REACHABILITY",
        "CLU.P.K_DISTANCE",
    ):
        assert artefact in src
    assert 'family === "clustering"' in src
    assert "runClusterPlot" in src


def test_api_exports_clustering_plot_paths() -> None:
    api = API.read_text(encoding="utf-8")
    assert "unsupervisedClusteringPlotPath" in api
    assert "runUnsupervisedClusteringPlot" in api
    assert "ClusteringCataloguePlot" in api