"""OPS.JOB.RELIABILITY — ST-OPS-03 heartbeat, reaper, idempotency (oneshot-c154)."""

from __future__ import annotations

from pathlib import Path

import pytest
from labcore.ops.job_reliability_contract import (
    ARTEFACT_ID,
    HEARTBEAT_INTERVAL_S,
    STALE_HEARTBEAT_S,
    JobReliabilityContractError,
    assert_job_reliability_contract,
    job_reliability_manifest,
)

ROOT = Path(__file__).resolve().parents[2]


def test_ops03_contract_passes() -> None:
    record = assert_job_reliability_contract()
    assert record["heartbeat_interval_s"] == HEARTBEAT_INTERVAL_S
    assert record["stale_heartbeat_s"] == STALE_HEARTBEAT_S


def test_manifest_seed_42() -> None:
    manifest = job_reliability_manifest(seed=42)
    assert manifest["id"] == ARTEFACT_ID
    assert manifest["seed"] == 42
    assert manifest["stress_id"] == "ST-OPS-03"


def test_fails_when_celery_acks_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    bad = tmp_path / "celery_app.py"
    bad.write_text("task_acks_late=False\n", encoding="utf-8")

    def fake_read(rel: str) -> str:
        if rel == "backend/worker/celery_app.py":
            return bad.read_text(encoding="utf-8")
        return (ROOT / rel).read_text(encoding="utf-8")

    import labcore.ops.job_reliability_contract as mod

    monkeypatch.setattr(mod, "_read", fake_read)
    with pytest.raises(JobReliabilityContractError, match="task_acks_late"):
        mod.assert_celery_acks_late()