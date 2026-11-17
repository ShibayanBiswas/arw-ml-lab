"""Locust public API scenario (LOAD.P.HEALTHZ_CATALOG / oneshot-c144)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("AUTH_TEST_BYPASS", "true")
os.environ.setdefault("AI_ENABLED", "false")
os.environ.setdefault("LAB_DEFAULT_SEED", "42")

from backend.app.main import create_app  # noqa: E402

LOCUSTFILE = Path(__file__).resolve().parents[1] / "load" / "locustfile.py"
SCENARIO_ID = "LOAD.P.HEALTHZ_CATALOG"
PUBLIC_PATHS = (
    "/healthz",
    "/api/v1/catalog",
    "/api/v1/catalog/algorithms",
    "/api/v1/catalog/metrics",
)


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


def test_locustfile_declares_scenario_without_secrets() -> None:
    text = LOCUSTFILE.read_text(encoding="utf-8")
    assert f'LOAD_SCENARIO_ID = "{SCENARIO_ID}"' in text
    for path in PUBLIC_PATHS:
        assert path in text
    assert 'headers={"Authorization"' not in text
    assert "Bearer " not in text
    assert "self.client.post" not in text


def test_lab_api_public_paths_match_locust_contract(client: TestClient) -> None:
    hz = client.get("/healthz")
    assert hz.status_code == 200
    assert hz.json()["seed"] == 42

    root = client.get("/api/v1/catalog")
    assert root.status_code == 200
    body = root.json()
    assert "algorithms" in body
    assert "metrics" in body

    algos = client.get("/api/v1/catalog/algorithms")
    assert algos.status_code == 200
    assert isinstance(algos.json(), list)
    assert len(algos.json()) >= 1

    metrics = client.get("/api/v1/catalog/metrics")
    assert metrics.status_code == 200
    assert isinstance(metrics.json(), list)