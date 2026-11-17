"""Reports templates workbench wires REP.T.FORMULAS (oneshot-c146)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WB = ROOT / "frontend" / "src" / "components" / "reports" / "ReportsWorkbench.tsx"
PANEL = ROOT / "frontend" / "src" / "components" / "reports" / "FormulaSheetPanel.tsx"
API = ROOT / "frontend" / "src" / "lib" / "api.ts"


def test_reports_workbench_wires_templates_formulas() -> None:
    wb = WB.read_text(encoding="utf-8")
    assert "FormulaSheetPanel" in wb
    assert 'mode === "templates"' in wb


def test_formula_panel_calls_formulas_api() -> None:
    panel = PANEL.read_text(encoding="utf-8")
    assert "runReportsFormulas" in panel
    assert "REP.T.FORMULAS" in panel


def test_api_exports_reports_formulas_client() -> None:
    api = API.read_text(encoding="utf-8")
    assert "reportsFormulasPath" in api
    assert "runReportsFormulas" in api
    assert "/api/v1/reports/formulas" in api