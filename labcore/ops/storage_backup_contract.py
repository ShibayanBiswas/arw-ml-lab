"""Supabase Storage off-site backup contract (ARCHITECTURE §46.2 OPS-13 / ST-OPS-06).

Postgres PITR does not cover Storage objects in ``models/`` and ``datasets/``.
DEPLOY_CONTABO §10 documents nightly rclone copies; this module is the offline kit
check that buckets, runbook text and bootstrap layout match the spec.
"""

from __future__ import annotations

import re
from pathlib import Path

ARTEFACT_ID = "OPS.STORAGE.BACKUP"
MI_RULE = "OPS-13"
STRESS_ID = "ST-OPS-06"
SEED_DEFAULT = 42

# Supabase Storage buckets mirrored off-site (not covered by DB backups).
STORAGE_MIRROR_BUCKETS: tuple[str, ...] = ("models", "datasets")
RCLONE_REMOTE_PATTERN = re.compile(r"rclone\s+copy", re.IGNORECASE)
BUCKET_PATH_PATTERN = re.compile(
    r"(`)?(models|datasets)/(`)?",
    re.IGNORECASE,
)
RESTORE_DRILL_PATTERN = re.compile(r"restore drill", re.IGNORECASE)
_BOOTSTRAP_BACKUPS = re.compile(
    r'\$APP_DIR/backups|"?\$APP_DIR"?/backups|/opt/arw-ml-lab/backups',
)
_BUCKET_INSERT = re.compile(
    r"\(\s*['\"]?(models|datasets)['\"]?\s*,",
    re.IGNORECASE,
)


class StorageBackupContractError(ValueError):
    """Raised when ST-OPS-06 / OPS-13 offline backup wiring is incomplete."""


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def assert_deploy_contabo_storage_section(
    doc_path: Path | None = None,
) -> dict[str, str]:
    """DEPLOY_CONTABO §10 must document rclone copies for models/datasets + restore drill."""
    path = doc_path or (_repo_root() / "docs" / "DEPLOY_CONTABO.md")
    if not path.is_file():
        msg = f"DEPLOY_CONTABO.md missing: {path}"
        raise StorageBackupContractError(msg)
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if "## 10. Backups" not in text:
        errors.append("DEPLOY_CONTABO.md: missing §10 Backups")
    section = text.split("## 10. Backups", 1)[-1].split("## 11.", 1)[0]
    if not RCLONE_REMOTE_PATTERN.search(section):
        errors.append("DEPLOY_CONTABO §10: must document rclone copy for off-site backups")
    for bucket in STORAGE_MIRROR_BUCKETS:
        if bucket not in section:
            errors.append(f"DEPLOY_CONTABO §10: must mention Storage bucket {bucket!r}")
    if not RESTORE_DRILL_PATTERN.search(section):
        errors.append("DEPLOY_CONTABO §10: must document a restore drill")
    if errors:
        raise StorageBackupContractError("; ".join(errors))
    return {
        "runbook": path.name,
        "section": "10",
        "buckets": ",".join(STORAGE_MIRROR_BUCKETS),
        "stress_id": STRESS_ID,
    }


def assert_deploy_md_ops13_pointer(deploy_path: Path | None = None) -> dict[str, str]:
    """``docs/DEPLOY.md`` must point readers at OPS-13 / Contabo Storage backups."""
    path = deploy_path or (_repo_root() / "docs" / "DEPLOY.md")
    if not path.is_file():
        msg = f"DEPLOY.md missing: {path}"
        raise StorageBackupContractError(msg)
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if "OPS-13" not in text and "ST-OPS-06" not in text:
        errors.append("DEPLOY.md: must reference OPS-13 or ST-OPS-06")
    has_contabo_link = "DEPLOY_CONTABO" in text or "DEPLOY_CONTABO.md" in text
    has_backups_section = "§10" in text or "10. Backups" in text
    if not (has_contabo_link and has_backups_section):
        errors.append("DEPLOY.md: must link DEPLOY_CONTABO §10 Storage backups")
    if errors:
        raise StorageBackupContractError("; ".join(errors))
    return {"deploy_guide": path.name, "ops_rule": MI_RULE}


def assert_storage_buckets_migration(
    migration_path: Path | None = None,
) -> dict[str, str]:
    """Core migration must declare ``models`` and ``datasets`` Storage buckets."""
    path = migration_path or (
        _repo_root() / "supabase" / "migrations" / "20261114000200_storage_buckets.sql"
    )
    if not path.is_file():
        msg = f"storage buckets migration missing: {path}"
        raise StorageBackupContractError(msg)
    text = path.read_text(encoding="utf-8")
    found: set[str] = set()
    for match in _BUCKET_INSERT.finditer(text):
        found.add(match.group(1).lower())
    missing = [b for b in STORAGE_MIRROR_BUCKETS if b not in found]
    if missing:
        raise StorageBackupContractError(
            f"{path.name}: missing bucket inserts for {', '.join(missing)}"
        )
    return {"migration": path.name, "buckets": ",".join(STORAGE_MIRROR_BUCKETS)}


def assert_bootstrap_backups_directory(
    bootstrap_path: Path | None = None,
) -> dict[str, str]:
    """Bootstrap must create ``/opt/arw-ml-lab/backups`` for local tarballs before rclone."""
    path = bootstrap_path or (_repo_root() / "scripts" / "bootstrap_contabo.sh")
    if not path.is_file():
        msg = f"bootstrap_contabo.sh missing: {path}"
        raise StorageBackupContractError(msg)
    text = path.read_text(encoding="utf-8")
    if not _BOOTSTRAP_BACKUPS.search(text):
        raise StorageBackupContractError(
            f"{path.name}: must create APP_DIR/backups (ST-OPS-06 local staging)"
        )
    return {"bootstrap": path.name, "local_staging": "backups/"}


def assert_storage_backup_contract(
    *,
    doc_path: Path | None = None,
    deploy_path: Path | None = None,
    migration_path: Path | None = None,
    bootstrap_path: Path | None = None,
) -> list[dict[str, str]]:
    """Run all ST-OPS-06 offline Storage backup checks."""
    return [
        assert_deploy_contabo_storage_section(doc_path),
        assert_deploy_md_ops13_pointer(deploy_path),
        assert_storage_buckets_migration(migration_path),
        assert_bootstrap_backups_directory(bootstrap_path),
    ]


def storage_backup_manifest(*, seed: int = SEED_DEFAULT) -> dict[str, object]:
    checks = assert_storage_backup_contract()
    return {
        "id": ARTEFACT_ID,
        "seed": seed,
        "stress_id": STRESS_ID,
        "ops_rule": MI_RULE,
        "mirror_buckets": list(STORAGE_MIRROR_BUCKETS),
        "checks": checks,
    }