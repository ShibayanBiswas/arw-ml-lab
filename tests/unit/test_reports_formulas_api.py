"""Reports formulas API artefact id (REP.T.FORMULAS / oneshot-c146)."""

from __future__ import annotations

import os

from fastapi.testclient import TestClient

os.environ["AUTH_TEST_BYPASS"] = "true"
os.environ["AI_ENABLED"] = "false"
os.environ["LAB_DEFAULT_SEED"] = "42"

from backend.app.main import create_app  # noqa: E402


def _headers() -> dict[str, str]:
    return {
        "Authorization": "Bearer test",
        "X-Test-Role": "analyst",
        "X-Test-User-Id": "00000000-0000-0000-0000-000000000099",
        "X-Test-Workspace-Id": "00000000-0000-0000-0000-000000000010",
    }


def test_reports_formulas_returns_rep_t_formulas() -> None:
    client = TestClient(create_app())
    r = client.post(
        "/api/v1/reports/formulas",
        headers=_headers(),
        json={"title": "Demo", "families": ["regression"]},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == "REP.T.FORMULAS"
    assert body["seed"] == 42
    assert "REP.T.FORMULAS" in body["html"]
    assert body["numbers"]["count"] == 5
    assert all(e["family"] == "regression" for e in body["entries"])