"""Reports bundle API artefact id (REP.T.BUNDLE / oneshot-c178)."""

from __future__ import annotations

import base64
import json
import os
import zipfile
from io import BytesIO

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


def test_reports_bundle_returns_rep_t_bundle() -> None:
    client = TestClient(create_app())
    r = client.post(
        "/api/v1/reports/bundle",
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
    assert body["id"] == "REP.T.BUNDLE"
    assert body["seed"] == 42
    assert body["timezone"] == "Asia/Kolkata"
    blob = base64.standard_b64decode(body["zip_base64"])
    with zipfile.ZipFile(BytesIO(blob)) as zf:
        manifest = json.loads(zf.read("manifest.json"))
        assert manifest["id"] == "REP.T.BUNDLE"
        assert manifest["timezone"] == "Asia/Kolkata"