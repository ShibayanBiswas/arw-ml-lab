"""Phase 0 API: healthz, catalog, RBAC viewer-deny, demo job + SSE."""

from __future__ import annotations

import json
import os

import pytest
from fastapi.testclient import TestClient

# Eager Celery + test auth before app import side effects
os.environ["AUTH_TEST_BYPASS"] = "true"
os.environ["AI_ENABLED"] = "false"
os.environ["LAB_DEFAULT_SEED"] = "42"

from backend.app.main import create_app  # noqa: E402
from backend.worker.celery_app import celery_app  # noqa: E402

celery_app.conf.task_always_eager = True
celery_app.conf.task_eager_propagates = True


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


def _headers(role: str) -> dict[str, str]:
    return {
        "Authorization": "Bearer test",
        "X-Test-Role": role,
        "X-Test-User-Id": "00000000-0000-0000-0000-000000000099",
        "X-Test-Workspace-Id": "00000000-0000-0000-0000-000000000010",
    }


def test_healthz(client: TestClient) -> None:
    r = client.get("/healthz")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["seed"] == 42


def test_catalog_empty(client: TestClient) -> None:
    r = client.get("/api/v1/catalog/algorithms")
    assert r.status_code == 200
    assert r.json() == []


def test_viewer_denied_on_post(client: TestClient) -> None:
    r = client.post("/api/v1/jobs/demo", headers=_headers("viewer"))
    assert r.status_code == 403


def test_analyst_demo_job_and_sse(client: TestClient) -> None:
    r = client.post(
        "/api/v1/jobs/demo",
        headers={**_headers("analyst"), "Idempotency-Key": "demo-1"},
    )
    assert r.status_code == 202
    job_id = r.json()["job_id"]

    # Idempotent replay
    r2 = client.post(
        "/api/v1/jobs/demo",
        headers={**_headers("analyst"), "Idempotency-Key": "demo-1"},
    )
    assert r2.json()["job_id"] == job_id

    status = client.get(f"/api/v1/jobs/{job_id}", headers=_headers("analyst"))
    assert status.status_code == 200
    assert status.json()["status"] == "done"
    assert status.json()["progress"] == 1.0

    with client.stream(
        "GET", f"/api/v1/jobs/{job_id}/events", headers=_headers("analyst")
    ) as stream:
        text = "".join(stream.iter_text())
    assert "event: done" in text or "event: progress" in text
    assert "data:" in text
    # Ensure JSON payloads parse
    for line in text.splitlines():
        if line.startswith("data:"):
            json.loads(line[len("data:") :].strip())


def test_me_requires_auth_without_bypass(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUTH_TEST_BYPASS", "false")
    from backend.app.settings import get_settings

    get_settings.cache_clear()
    c = TestClient(create_app())
    r = c.get("/api/v1/auth/me")
    assert r.status_code == 401
    get_settings.cache_clear()
    os.environ["AUTH_TEST_BYPASS"] = "true"
