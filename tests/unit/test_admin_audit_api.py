"""Admin audit API (ENT.T.AUDIT_LOG / oneshot-c143)."""

from __future__ import annotations

import os

from fastapi.testclient import TestClient

os.environ["AUTH_TEST_BYPASS"] = "true"
os.environ["AI_ENABLED"] = "false"
os.environ["LAB_DEFAULT_SEED"] = "42"

from backend.app.main import create_app  # noqa: E402

WS = "00000000-0000-0000-0000-000000000010"


def _headers(role: str = "admin") -> dict[str, str]:
    return {
        "Authorization": "Bearer test",
        "X-Test-Role": role,
        "X-Test-User-Id": "00000000-0000-0000-0000-000000000099",
        "X-Test-Workspace-Id": WS,
    }


def test_admin_audit_list_ent_t_audit_log() -> None:
    client = TestClient(create_app())
    r = client.get("/api/v1/admin/audit", headers=_headers("admin"))
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == "ENT.T.AUDIT_LOG"
    assert body["seed"] == 42
    assert body["count"] >= 1
    assert body["rows"][0]["action"]


def test_admin_audit_forbidden_for_viewer() -> None:
    client = TestClient(create_app())
    r = client.get("/api/v1/admin/audit", headers=_headers("viewer"))
    assert r.status_code == 403


def test_admin_audit_export_csv() -> None:
    client = TestClient(create_app())
    r = client.get("/api/v1/admin/audit/export", headers=_headers("owner"))
    assert r.status_code == 200
    assert "text/csv" in r.headers.get("content-type", "")
    assert r.headers.get("X-Artefact-Id") == "ENT.T.AUDIT_EXPORT"
    assert "action" in r.text.splitlines()[0]