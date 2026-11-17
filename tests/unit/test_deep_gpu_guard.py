"""DEEP.GPU.GUARD — GPU worker HTTP 422 guard (oneshot-c159)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from labcore.deep.gpu_guard_contract import (
    ARTEFACT_ID,
    HTTP_STATUS,
    gpu_guard_manifest,
    gpu_only_algorithm_keys,
    validate_train_gpu_guard,
)
from labcore.deep.guards import gpu_worker_available


def test_gpu_only_keys_include_xlstm():
    keys = gpu_only_algorithm_keys()
    assert "seq.xlstm" in keys
    assert "dl.tabpfn" not in keys


def test_validate_raises_without_worker(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("LAB_GPU_WORKER", raising=False)
    assert gpu_worker_available() is False
    with pytest.raises(ValueError, match="GPU worker"):
        validate_train_gpu_guard(["seq.xlstm"])
    validate_train_gpu_guard(["clf.logistic"])


def test_manifest_offline_seed_42(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("LAB_GPU_WORKER", raising=False)
    m = gpu_guard_manifest(seed=42)
    assert m["id"] == ARTEFACT_ID
    assert m["http_status"] == HTTP_STATUS
    assert m["seed"] == 42
    assert m["worker_available"] is False
    assert "seq.xlstm" in m["gpu_only_keys"]


def test_api_gpu_model_returns_422(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("AUTH_TEST_BYPASS", "true")
    monkeypatch.delenv("LAB_GPU_WORKER", raising=False)
    from backend.app.dataset_store import DATASET_STORE
    from backend.app.main import create_app

    rec = DATASET_STORE.create_dataset(
        workspace_id="00000000-0000-0000-0000-000000000010",
        name="gpu-guard-c159",
        source="sample",
        sample_id=None,
        storage_key=None,
        parquet_path=None,
        content_hash=None,
    )
    client = TestClient(create_app())
    headers = {
        "Authorization": "Bearer test",
        "X-Test-Role": "analyst",
        "X-Test-User-Id": "00000000-0000-0000-0000-000000000099",
        "X-Test-Workspace-Id": "00000000-0000-0000-0000-000000000010",
    }
    r = client.post(
        "/api/v1/experiments/train",
        json={
            "dataset_id": rec.id,
            "target": "y",
            "task": "regression",
            "algorithm_keys": ["seq.xlstm"],
        },
        headers=headers,
    )
    assert r.status_code == 422, r.text
    assert "GPU" in r.json()["detail"]