"""Reports templates workbench wires REP.T.EXECUTIVE (oneshot-c142)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WB = ROOT / "frontend" / "src" / "components" / "reports" / "ReportsWorkbench.tsx"
PANEL = ROOT / "frontend" / "src" / "components" / "reports" / "ExecutiveSummaryPanel.tsx"
API = ROOT / "frontend" / "src" / "lib" / "api.ts"


def test_reports_workbench_wires_templates_executive() -> None:
    wb = WB.read_text(encoding="utf-8")
    panel = PANEL.read_text(encoding="utf-8")
    assert "ExecutiveSummaryPanel" in wb
    assert "templates" in wb
    assert "REP.T.EXECUTIVE" in panel


def test_api_exports_reports_executive_client() -> None:
    api = API.read_text(encoding="utf-8")
    assert "reportsExecutivePath" in api
    assert "runReportsExecutive" in api
    assert "/api/v1/reports/executive" in api