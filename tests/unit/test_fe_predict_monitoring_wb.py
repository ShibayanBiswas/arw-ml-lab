"""Predict monitoring workbench wires MON.T.KS_DRIFT + MON.T.PSI_DRIFT (c139/c140)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WB = ROOT / "frontend" / "src" / "components" / "predict" / "PredictWorkbench.tsx"
PANEL = ROOT / "frontend" / "src" / "components" / "predict" / "MonitoringDriftPanel.tsx"
API = ROOT / "frontend" / "src" / "lib" / "api.ts"


def test_predict_workbench_wires_monitoring_mode() -> None:
    src = WB.read_text(encoding="utf-8")
    assert "MonitoringDriftPanel" in src
    assert 'effectiveMode === "monitoring"' in src


def test_monitoring_panel_calls_ks_api() -> None:
    panel = PANEL.read_text(encoding="utf-8")
    assert "runMonitoringKsDrift" in panel
    assert "MON.T.KS_DRIFT" in panel


def test_api_exports_monitoring_ks_client() -> None:
    api = API.read_text(encoding="utf-8")
    assert "monitoringKsDriftPath" in api
    assert "runMonitoringKsDrift" in api
    assert "/api/v1/monitoring/drift/ks" in api


def test_monitoring_panel_calls_psi_api() -> None:
    panel = PANEL.read_text(encoding="utf-8")
    assert "runMonitoringPsiDrift" in panel
    assert "MON.T.PSI_DRIFT" in panel


def test_api_exports_monitoring_psi_client() -> None:
    api = API.read_text(encoding="utf-8")
    assert "monitoringPsiDriftPath" in api
    assert "runMonitoringPsiDrift" in api
    assert "/api/v1/monitoring/drift/psi" in api