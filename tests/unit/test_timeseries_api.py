"""Phase 4 thin API — HorizonGuard 422 when h > h_max."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

os.environ["AUTH_TEST_BYPASS"] = "true"
os.environ["LAB_DEFAULT_SEED"] = "42"


@pytest.fixture()
def client() -> TestClient:
    from backend.app.main import create_app

    return TestClient(create_app())


def _auth() -> dict[str, str]:
    return {
        "Authorization": "Bearer test",
        "X-Test-Role": "scientist",
        "X-Test-User-Id": "00000000-0000-0000-0000-000000000099",
        "X-Test-Workspace-Id": "00000000-0000-0000-0000-000000000010",
    }


def test_horizon_ds22(client: TestClient):
    r = client.post(
        "/api/v1/timeseries/horizon",
        headers=_auth(),
        json={"sample_id": "DS22"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["h_max"] == 24


def test_horizon_over_max_422(client: TestClient):
    r = client.post(
        "/api/v1/timeseries/horizon",
        headers=_auth(),
        json={"sample_id": "DS22", "h_request": 100},
    )
    assert r.status_code == 422, r.text


def test_backtest_over_max_422(client: TestClient):
    r = client.post(
        "/api/v1/timeseries/backtest",
        headers=_auth(),
        json={"sample_id": "DS22", "h": 100, "w": 4, "m": 12},
    )
    assert r.status_code == 422, r.text
