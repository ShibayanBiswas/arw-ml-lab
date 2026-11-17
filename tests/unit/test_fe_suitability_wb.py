"""Suitability workbench exposes FS.P catalogue actions (oneshot-c134)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WB = ROOT / "frontend" / "src" / "components" / "finance" / "SuitabilityWorkbench.tsx"
API = ROOT / "frontend" / "src" / "lib" / "api.ts"


def test_suitability_workbench_wires_fs_catalogue() -> None:
    src = WB.read_text(encoding="utf-8")
    assert "runSuitabilityPlot" in src
    for artefact in (
        "FS.P.VOL",
        "FS.P.PRICE",
        "FS.P.BARRIERS",
        "FS.P.UNIQUENESS",
        "FS.P.HOLDING",
        "FS.P.MIN_FFD",
        "FS.P.SADF",
        "FS.P.TRENDSCAN",
        "FS.P.LABEL_BALANCE",
        "FS.P.GRID",
    ):
        assert artefact in src
    assert "runPlot" in src


def test_api_exports_suitability_plot_paths() -> None:
    api = API.read_text(encoding="utf-8")
    assert "suitabilityPlotPath" in api
    assert "runSuitabilityPlot" in api
    assert "SuitabilityCataloguePlot" in api