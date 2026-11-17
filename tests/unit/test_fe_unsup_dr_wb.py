"""DR workbench exposes DR.P catalogue actions (oneshot-c133)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WB = ROOT / "frontend" / "src" / "components" / "unsupervised" / "UnsupervisedWorkbench.tsx"
API = ROOT / "frontend" / "src" / "lib" / "api.ts"


def test_dr_workbench_wires_dr_catalogue() -> None:
    src = WB.read_text(encoding="utf-8")
    assert "runUnsupervisedDrPlot" in src
    for artefact in (
        "DR.P.SCREE",
        "DR.P.CUMVAR",
        "DR.P.BIPLOT",
        "DR.P.LOADINGS",
        "DR.P.CORR_CIRCLE",
    ):
        assert artefact in src
    assert 'family === "dr"' in src
    assert "runDrPlot" in src


def test_api_exports_dr_plot_paths() -> None:
    api = API.read_text(encoding="utf-8")
    assert "unsupervisedDrPlotPath" in api
    assert "runUnsupervisedDrPlot" in api
    assert "DrCataloguePlot" in api