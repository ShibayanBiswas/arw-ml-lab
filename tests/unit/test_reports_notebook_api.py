"""Reports notebook API artefact id (REP.T.NOTEBOOK / oneshot-c141)."""

from __future__ import annotations

import os

import nbformat
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


def test_reports_notebook_returns_rep_t_notebook() -> None:
    client = TestClient(create_app())
    r = client.post(
        "/api/v1/reports/notebook",
        headers=_headers(),
        json={
            "title": "DS1",
            "dataset_id": "DS1",
            "algorithm_key": "lightgbm",
            "facts": {"seed": 42, "split": "oof"},
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == "REP.T.NOTEBOOK"
    assert body["seed"] == 42
    text = body["nbformat_json"]
    assert "DS1" in text and "lightgbm" in text
    nb = nbformat.reads(text, as_version=4)
    nbformat.validate(nb)