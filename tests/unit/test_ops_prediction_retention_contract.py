"""OPS.PREDICTION.RETENTION — ST-OPS-07 prediction retention contract (oneshot-c156)."""

from __future__ import annotations

from pathlib import Path

import pytest

from labcore.ops.prediction_retention_contract import (
    ARTEFACT_ID,
    PREDICTION_RESULTS_CAP,
    PREDICTION_RETENTION_DAYS,
    PredictionRetentionContractError,
    assert_hardening_expired_prediction_jobs,
    assert_maintenance_prediction_retention,
    assert_prediction_migration_expires_at,
    assert_prediction_retention_contract,
    prediction_retention_manifest,
)

ROOT = Path(__file__).resolve().parents[2]


def test_repo_prediction_retention_contract() -> None:
    contract = assert_prediction_retention_contract()
    assert contract["expires_at"]["retention_days"] == PREDICTION_RETENTION_DAYS
    assert contract["maintenance"]["results_cap"] == PREDICTION_RESULTS_CAP


def test_prediction_migration_and_hardening() -> None:
    mig = assert_prediction_migration_expires_at()
    fn = assert_hardening_expired_prediction_jobs()
    assert "prediction_studio" in mig["migration"]
    assert fn["function"] == "expired_prediction_jobs"


def test_maintenance_module_constants() -> None:
    worker = assert_maintenance_prediction_retention()
    assert worker["retention_days"] == 30
    assert worker["results_cap"] == 1000


def test_rejects_maintenance_without_storage_purge(tmp_path: Path) -> None:
    good = (ROOT / "backend/worker/maintenance.py").read_text(encoding="utf-8")
    stripped = good.replace("purge_prediction_storage(keys)", "")
    bad = tmp_path / "maintenance.py"
    bad.write_text(stripped, encoding="utf-8")

    import labcore.ops.prediction_retention_contract as mod

    real_read = mod._read

    def patched_read(rel: str) -> str:
        if rel == "backend/worker/maintenance.py":
            return bad.read_text(encoding="utf-8")
        return real_read(rel)

    mod._read = patched_read
    try:
        with pytest.raises(PredictionRetentionContractError, match="purge Storage"):
            assert_maintenance_prediction_retention()
    finally:
        mod._read = real_read


def test_manifest_contract_seed_42() -> None:
    manifest = prediction_retention_manifest(seed=42)
    assert manifest["id"] == ARTEFACT_ID
    assert manifest["seed"] == 42
    assert manifest["stress_id"] == "ST-OPS-07"
    assert manifest["maintenance"]["results_cap"] == PREDICTION_RESULTS_CAP