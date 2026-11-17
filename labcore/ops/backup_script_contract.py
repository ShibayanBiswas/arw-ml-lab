"""scripts/backup_contabo.sh must match DEPLOY_CONTABO §10 — OPS.BACKUP.SCRIPT (oneshot-c221)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

ARTEFACT_ID = "OPS.BACKUP.SCRIPT"
REQUIRED_TOKENS = (
    "redis-cli",
    "BGSAVE",
    "rclone",
    "models",
    "datasets",
    "backups",
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def assert_deploy_doc_points_at_script() -> dict[str, str]:
    text = (_repo_root() / "docs" / "DEPLOY_CONTABO.md").read_text(encoding="utf-8")
    if "backup_contabo.sh" not in text:
        raise AssertionError("DEPLOY_CONTABO §10 must name scripts/backup_contabo.sh")
    return {"doc": "DEPLOY_CONTABO.md"}


def assert_backup_script() -> dict[str, Any]:
    path = _repo_root() / "scripts" / "backup_contabo.sh"
    if not path.is_file():
        raise AssertionError("scripts/backup_contabo.sh missing")
    text = path.read_text(encoding="utf-8")
    missing = [t for t in REQUIRED_TOKENS if t not in text]
    if missing:
        raise AssertionError(f"backup script missing tokens: {missing}")
    if "REDIS_PASSWORD" not in text:
        raise AssertionError("backup script must use REDIS_PASSWORD from .env (not print it)")
    doc = assert_deploy_doc_points_at_script()
    return {
        "id": ARTEFACT_ID,
        "seed": 42,
        "path": "scripts/backup_contabo.sh",
        "tokens": list(REQUIRED_TOKENS),
        "doc": doc,
    }
