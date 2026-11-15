"""Unit tests for intake detectors and confirm guards."""

from __future__ import annotations

import pandas as pd
import pytest
from backend.app.main import create_app
from fastapi.testclient import TestClient
from labcore.data.samples import load_sample_frame
from labcore.intake.d1_datetime import detect_datetime_index
from labcore.intake.d7_diff import schema_diff
from labcore.intake.pipeline import run_intake
from labcore.intake.profile import extended_profile
from labcore.intake.validator import confirm_guard


def test_ambiguous_date_day_month_le_12():
    df = pd.DataFrame(
        {
            "event_date": ["01/02/2024", "03/04/2024", "05/06/2024", "07/08/2024"] * 5,
            "y": range(20),
        }
    )
    profile = extended_profile(df)
    d1 = detect_datetime_index(df, profile)
    assert any(
        "ambiguous" in q.lower() or "≤ 12" in q or "<= 12" in q for q in d1["questions"]
    ) or (d1.get("accepted") and d1["accepted"].get("ambiguous_format"))


def test_confirm_hard_exclude_raises():
    df, _, _ = load_sample_frame("DS3")
    result = run_intake(df)
    merged = result["merged"]
    roles = merged["roles"]
    # force include PassengerId
    merged.setdefault("user_overrides", {})["roles"] = {"PassengerId": {"included": True}}
    with pytest.raises(ValueError, match="hard-excluded"):
        confirm_guard(merged, roles)


def test_schema_diff_rename_and_breaking():
    parent = pd.DataFrame(
        {
            "Date": pd.date_range("2020-01-01", periods=30, freq="B"),
            "Close": range(30),
            "Volume": range(30),
        }
    )
    renamed = parent.rename(columns={"Volume": "Vol"})
    diff = schema_diff(parent, renamed)
    assert any(r.get("from") == "Volume" and r.get("to") == "Vol" for r in diff["renames"])

    broken = parent.copy()
    broken["Close"] = broken["Close"].astype(str)
    diff2 = schema_diff(parent, broken)
    assert diff2["breaking"] is True
    assert any(
        c.get("kind") == "type_change" and c.get("column") == "Close" for c in diff2["changes"]
    )


def test_nifty_append_compatible_diff():
    df, _, _ = load_sample_frame("DS30")
    parent = df.iloc[:100].copy()
    child = pd.concat([parent, df.iloc[100:120]], ignore_index=True)
    diff = schema_diff(parent, child)
    assert diff["compatible"] is True
    assert diff["breaking"] is False


def test_api_confirm_hard_exclude_422() -> None:
    import os

    os.environ["AUTH_TEST_BYPASS"] = "true"
    os.environ["AI_ENABLED"] = "false"
    from backend.worker.celery_app import celery_app

    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
    client = TestClient(create_app())
    headers = {
        "Authorization": "Bearer test",
        "X-Test-Role": "scientist",
        "X-Test-User-Id": "00000000-0000-0000-0000-000000000099",
        "X-Test-Workspace-Id": "00000000-0000-0000-0000-000000000010",
    }
    r = client.post("/api/v1/datasets/samples/DS3/load", headers=headers)
    assert r.status_code == 202
    job_id = r.json()["job_id"]
    job = client.get(f"/api/v1/jobs/{job_id}", headers=headers).json()
    for _ in range(50):
        job = client.get(f"/api/v1/jobs/{job_id}", headers=headers).json()
        if job["status"] in {"done", "error"}:
            break
    assert job["status"] == "done"
    ds_id = job["result"]["dataset_id"]
    ir = client.get(f"/api/v1/intake/{ds_id}", headers=headers)
    if ir.status_code == 404:
        run = client.post(
            f"/api/v1/intake/{ds_id}/run",
            headers={**headers, "Content-Type": "application/json"},
            json={"use_llm": False},
        )
        assert run.status_code == 202
        jid = run.json()["job_id"]
        for _ in range(50):
            j = client.get(f"/api/v1/jobs/{jid}", headers=headers).json()
            if j["status"] in {"done", "error"}:
                break
        ir = client.get(f"/api/v1/intake/{ds_id}", headers=headers)
    assert ir.status_code == 200
    proposal = ir.json()
    pid = proposal["id"]
    client.patch(
        f"/api/v1/intake/proposals/{pid}",
        headers={**headers, "Content-Type": "application/json"},
        json={"overrides": {"roles": {"PassengerId": {"included": True}}}},
    )
    bad = client.post(
        f"/api/v1/intake/proposals/{pid}/confirm",
        headers={**headers, "Content-Type": "application/json"},
        json={},
    )
    assert bad.status_code == 422
