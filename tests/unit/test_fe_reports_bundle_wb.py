"""Reports templates workbench wires REP.T.BUNDLE (oneshot-c178)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WB = ROOT / "frontend" / "src" / "components" / "reports" / "ReportsWorkbench.tsx"
PANEL = ROOT / "frontend" / "src" / "components" / "reports" / "ReproductionBundlePanel.tsx"
API = ROOT / "frontend" / "src" / "lib" / "api.ts"


def test_reports_workbench_wires_templates_bundle() -> None:
    src = WB.read_text(encoding="utf-8")
    assert "ReproductionBundlePanel" in src
    assert 'mode === "templates"' in src


def test_reproduction_bundle_panel_calls_api() -> None:
    panel = PANEL.read_text(encoding="utf-8")
    assert "runReportsBundle" in panel
    assert "REP.T.BUNDLE" in panel
    assert "Asia/Kolkata" in panel


def test_api_exports_reports_bundle_client() -> None:
    api = API.read_text(encoding="utf-8")
    assert "reportsBundlePath" in api
    assert "runReportsBundle" in api
    assert "/api/v1/reports/bundle" in api