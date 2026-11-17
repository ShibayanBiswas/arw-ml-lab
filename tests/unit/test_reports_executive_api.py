"""Reports executive API artefact id (REP.T.EXECUTIVE / oneshot-c142)."""

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


def test_reports_executive_returns_rep_t_executive() -> None:
    client = TestClient(create_app())
    r = client.post(
        "/api/v1/reports/executive",
        headers=_headers(),
        json={
            "title": "Demo",
            "stage": "supervised",
            "facts": {"seed": 42, "n_models": 1},
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == "REP.T.EXECUTIVE"
    assert body["seed"] == 42
    assert "REP.T.EXECUTIVE" in body["html"]
    assert "n_models" in body["html"]