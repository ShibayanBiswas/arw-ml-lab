"""Phase 1 API: sample load + EDA run."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

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


def _headers(role: str = "scientist") -> dict[str, str]:
    return {
        "Authorization": "Bearer test",
        "X-Test-Role": role,
        "X-Test-User-Id": "00000000-0000-0000-0000-000000000099",
        "X-Test-Workspace-Id": "00000000-0000-0000-0000-000000000010",
    }


def test_list_samples(client: TestClient) -> None:
    r = client.get("/api/v1/datasets/samples", headers=_headers())
    assert r.status_code == 200
    body = r.json()
    ids = {x["id"] for x in body}
    assert {"DS3", "DS22", "DS30"} <= ids


def test_load_ds3_and_run_eda(client: TestClient) -> None:
    r = client.post("/api/v1/datasets/samples/DS3/load", headers=_headers())
    assert r.status_code == 202
    job_id = r.json()["job_id"]
    job = client.get(f"/api/v1/jobs/{job_id}", headers=_headers()).json()
    assert job["status"] == "done"
    dataset_id = job["result"]["dataset_id"]

    preview = client.get(f"/api/v1/datasets/{dataset_id}/preview", headers=_headers())
    assert preview.status_code == 200
    schema = {c["name"]: c for c in preview.json()["schema"]}
    assert schema["Survived"]["semantic_type"] in {"boolean", "numeric_discrete"}
    assert schema["Name"]["semantic_type"] == "text"
    assert schema["Cabin"]["semantic_type"] == "high_cardinality"

    eda = client.post(f"/api/v1/eda/{dataset_id}/run", headers=_headers())
    assert eda.status_code == 202
    eda_job = eda.json()["job_id"]
    status = client.get(f"/api/v1/jobs/{eda_job}", headers=_headers()).json()
    assert status["status"] == "done"
    assert status["result"]["n_artefacts"] >= 19
    assert len(status["result"]["table_ids"]) == 19

    run = client.get(f"/api/v1/eda/by-job/{eda_job}", headers=_headers())
    assert run.status_code == 200
    insights = run.json()["insights"]
    cols = {i["column"] for i in insights if i.get("column")}
    assert "Age" in cols and "Cabin" in cols
