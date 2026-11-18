"""Deep ensemble smoke API — oneshot-c263."""

from __future__ import annotations

import os

os.environ["AUTH_TEST_BYPASS"] = "true"
os.environ.setdefault("AI_ENABLED", "false")
os.environ.setdefault("LAB_DEFAULT_SEED", "42")

from fastapi.testclient import TestClient

from backend.app.main import create_app


def test_deep_ensemble_smoke_endpoint() -> None:
    client = TestClient(create_app())
    res = client.post(
        "/api/v1/deep/ensemble/smoke",
        json={"seed": 42, "n_rows": 4},
        headers={
            "Authorization": "Bearer test",
            "X-Test-Role": "scientist",
            "X-Test-User-Id": "00000000-0000-0000-0000-000000000099",
            "X-Test-Workspace-Id": "00000000-0000-0000-0000-000000000010",
        },
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["id"] == "UQ.DEEP.ENSEMBLE"
    assert body["n_members"] == 2
    assert body["refit"] is False
