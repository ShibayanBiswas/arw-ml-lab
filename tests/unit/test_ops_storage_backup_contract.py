"""OPS.STORAGE.BACKUP — ST-OPS-06 / OPS-13 Storage mirror contract (oneshot-c162)."""

from __future__ import annotations

from pathlib import Path

import pytest

from labcore.ops.storage_backup_contract import (
    ARTEFACT_ID,
    STORAGE_MIRROR_BUCKETS,
    STRESS_ID,
    StorageBackupContractError,
    assert_bootstrap_backups_directory,
    assert_deploy_contabo_storage_section,
    assert_deploy_md_ops13_pointer,
    assert_storage_backup_contract,
    assert_storage_buckets_migration,
    storage_backup_manifest,
)

ROOT = Path(__file__).resolve().parents[2]


def test_repo_storage_backup_contract() -> None:
    checks = assert_storage_backup_contract()
    assert len(checks) == 4
    assert checks[0]["stress_id"] == STRESS_ID
    assert checks[2]["buckets"] == ",".join(STORAGE_MIRROR_BUCKETS)


def test_deploy_contabo_and_migration_individually() -> None:
    contabo = assert_deploy_contabo_storage_section(ROOT / "docs" / "DEPLOY_CONTABO.md")
    buckets = assert_storage_buckets_migration()
    assert contabo["section"] == "10"
    assert "models" in buckets["buckets"]


def test_rejects_runbook_without_rclone(tmp_path: Path) -> None:
    bad = tmp_path / "DEPLOY_CONTABO.md"
    bad.write_text(
        "## 10. Backups\n\nCopy models and datasets manually.\n\n## 11. Monitoring\n",
        encoding="utf-8",
    )
    with pytest.raises(StorageBackupContractError, match="rclone"):
        assert_deploy_contabo_storage_section(bad)


def test_rejects_migration_missing_datasets_bucket(tmp_path: Path) -> None:
    bad = tmp_path / "buckets.sql"
    bad.write_text("values ('models','models',false);\n", encoding="utf-8")
    with pytest.raises(StorageBackupContractError, match="datasets"):
        assert_storage_buckets_migration(bad)


def test_bootstrap_and_deploy_pointer() -> None:
    assert_bootstrap_backups_directory(ROOT / "scripts" / "bootstrap_contabo.sh")
    meta = assert_deploy_md_ops13_pointer(ROOT / "docs" / "DEPLOY.md")
    assert meta["ops_rule"] == "OPS-13"


def test_manifest_contract_seed_42() -> None:
    manifest = storage_backup_manifest(seed=42)
    assert manifest["id"] == ARTEFACT_ID
    assert manifest["seed"] == 42
    assert manifest["mirror_buckets"] == list(STORAGE_MIRROR_BUCKETS)
    assert len(manifest["checks"]) == 4