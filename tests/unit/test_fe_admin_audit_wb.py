"""Admin audit workbench wires ENT.T.AUDIT_LOG (oneshot-c143)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WB = ROOT / "frontend" / "src" / "components" / "admin" / "AdminWorkbench.tsx"
PANEL = ROOT / "frontend" / "src" / "components" / "admin" / "AuditLogPanel.tsx"
API = ROOT / "frontend" / "src" / "lib" / "api.ts"


def test_admin_workbench_wires_audit_panel() -> None:
    src = WB.read_text(encoding="utf-8")
    assert "AuditLogPanel" in src
    assert 'mode === "audit"' in src


def test_audit_panel_calls_admin_api() -> None:
    panel = PANEL.read_text(encoding="utf-8")
    assert "fetchAdminAuditLog" in panel
    assert "ENT.T.AUDIT_LOG" in panel
    assert "downloadAdminAuditExport" in panel


def test_api_exports_admin_audit_client() -> None:
    api = API.read_text(encoding="utf-8")
    assert "adminAuditPath" in api
    assert "fetchAdminAuditLog" in api
    assert "/api/v1/admin/audit" in api