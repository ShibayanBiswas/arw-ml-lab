"""Reports templates workbench wires REP.T.NOTEBOOK (oneshot-c141)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WB = ROOT / "frontend" / "src" / "components" / "reports" / "ReportsWorkbench.tsx"
PANEL = ROOT / "frontend" / "src" / "components" / "reports" / "ReproductionNotebookPanel.tsx"
API = ROOT / "frontend" / "src" / "lib" / "api.ts"


def test_reports_workbench_wires_templates_notebook() -> None:
    src = WB.read_text(encoding="utf-8")
    assert "ReproductionNotebookPanel" in src
    assert 'mode === "templates"' in src


def test_reproduction_panel_calls_notebook_api() -> None:
    panel = PANEL.read_text(encoding="utf-8")
    assert "runReportsNotebook" in panel
    assert "REP.T.NOTEBOOK" in panel


def test_api_exports_reports_notebook_client() -> None:
    api = API.read_text(encoding="utf-8")
    assert "reportsNotebookPath" in api
    assert "runReportsNotebook" in api
    assert "/api/v1/reports/notebook" in api