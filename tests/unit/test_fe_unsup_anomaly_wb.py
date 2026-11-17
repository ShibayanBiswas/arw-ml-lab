"""Anomaly workbench exposes full ANO.P catalogue (oneshot-c137)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WB = ROOT / "frontend" / "src" / "components" / "unsupervised" / "UnsupervisedWorkbench.tsx"
API = ROOT / "frontend" / "src" / "lib" / "api.ts"


def test_anomaly_workbench_wires_ano_catalogue() -> None:
    src = WB.read_text(encoding="utf-8")
    assert "runUnsupervisedAnomalyPlot" in src
    for artefact in (
        "ANO.P.SCORE_HIST",
        "ANO.P.RANKED",
        "ANO.P.EMBED",
        "ANO.P.PARETO",
        "ANO.P.PAIRWISE",
    ):
        assert artefact in src
    assert 'family === "anomaly"' in src
    assert "runPlot" in src


def test_api_exports_anomaly_plot_paths() -> None:
    api = API.read_text(encoding="utf-8")
    assert "unsupervisedAnomalyPlotPath" in api
    assert "runUnsupervisedAnomalyPlot" in api
    assert "AnomalyCataloguePlot" in api
    assert '"pareto"' in api
    assert '"pairwise"' in api