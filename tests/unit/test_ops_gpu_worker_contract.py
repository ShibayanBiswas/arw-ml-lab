"""OPS.GPU.WORKER — Contabo §12 LAB_GPU_WORKER=false / HTTP 422 (oneshot-c160)."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from labcore.deep.guards import assert_gpu_allowed, gpu_worker_available
from labcore.ops.gpu_worker_contract import (
    ARTEFACT_ID,
    DEFAULT_LAB_GPU_WORKER,
    ENV_LAB_GPU_WORKER,
    GpuWorkerContractError,
    assert_compose_lab_gpu_worker_false,
    assert_deploy_contabo_section12_gpu_422,
    assert_experiments_router_maps_gpu_to_422,
    assert_gpu_worker_contract,
    gpu_only_algorithm_keys,
    gpu_worker_manifest,
)

ROOT = Path(__file__).resolve().parents[2]


def test_repo_gpu_worker_contract() -> None:
    checks = assert_gpu_worker_contract()
    assert len(checks) >= 4
    assert "seq.xlstm" in gpu_only_algorithm_keys()


def test_rejects_compose_without_gpu_false(tmp_path: Path) -> None:
    bad = tmp_path / "docker-compose.prod.yml"
    bad.write_text(
        "services:\n  worker-train:\n    environment:\n      LAB_GPU_WORKER: 'true'\n",
        encoding="utf-8",
    )
    with pytest.raises(GpuWorkerContractError, match="false"):
        assert_compose_lab_gpu_worker_false(bad)


def test_deploy_contabo_and_router_individually() -> None:
    doc = assert_deploy_contabo_section12_gpu_422(ROOT / "docs" / "DEPLOY_CONTABO.md")
    router = assert_experiments_router_maps_gpu_to_422(
        ROOT / "backend" / "app" / "routers" / "experiments.py",
    )
    assert doc["section"] == "12"
    assert router["http_status"] == "422"


def test_manifest_contract_seed_42() -> None:
    manifest = gpu_worker_manifest(seed=42)
    assert manifest["id"] == ARTEFACT_ID
    assert manifest["seed"] == 42
    assert manifest[ENV_LAB_GPU_WORKER] == DEFAULT_LAB_GPU_WORKER
    assert "seq.xlstm" in manifest["gpu_only_algorithm_keys"]


def test_guard_raises_without_worker(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(ENV_LAB_GPU_WORKER, raising=False)
    assert gpu_worker_available() is False
    with pytest.raises(ValueError, match="GPU worker"):
        assert_gpu_allowed({"gpu": True})


def _gpu_guard_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("AUTH_TEST_BYPASS", "true")
    monkeypatch.delenv(ENV_LAB_GPU_WORKER, raising=False)
    from backend.app.dataset_store import DATASET_STORE
    from backend.app.main import create_app

    rec = DATASET_STORE.create_dataset(
        workspace_id="00000000-0000-0000-0000-000000000010",
        name="gpu-guard-c160",
        source="sample",
        sample_id=None,
        storage_key=None,
        parquet_path=None,
        content_hash=None,
    )
    client = TestClient(create_app())
    client._gpu_test_dataset_id = rec.id  # type: ignore[attr-defined]
    return client


def _headers() -> dict[str, str]:
    return {
        "Authorization": "Bearer test",
        "X-Test-Role": "analyst",
        "X-Test-User-Id": "00000000-0000-0000-0000-000000000099",
        "X-Test-Workspace-Id": "00000000-0000-0000-0000-000000000010",
    }


def test_api_train_gpu_model_returns_422(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _gpu_guard_client(monkeypatch)
    dataset_id = client._gpu_test_dataset_id  # type: ignore[attr-defined]
    r = client.post(
        "/api/v1/experiments/train",
        json={
            "dataset_id": dataset_id,
            "target": "y",
            "task": "regression",
            "algorithm_keys": ["seq.xlstm"],
        },
        headers=_headers(),
    )
    assert r.status_code == 422, r.text
    assert "GPU" in r.json()["detail"]


def test_api_tune_gpu_model_returns_422(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _gpu_guard_client(monkeypatch)
    dataset_id = client._gpu_test_dataset_id  # type: ignore[attr-defined]
    r = client.post(
        "/api/v1/experiments/tune",
        json={
            "dataset_id": dataset_id,
            "target": "y",
            "task": "regression",
            "algorithm_key": "seq.xlstm",
            "preset": "quick",
        },
        headers=_headers(),
    )
    assert r.status_code == 422, r.text
    assert "GPU" in r.json()["detail"]