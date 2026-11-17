"""Deploy workflow must scp backup_contabo.sh — OPS.DEPLOY.BACKUP_SCP (oneshot-c223)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

ARTEFACT_ID = "OPS.DEPLOY.BACKUP_SCP"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def assert_deploy_workflow_scps_backup() -> dict[str, Any]:
    text = (_repo_root() / ".github" / "workflows" / "deploy.yml").read_text(encoding="utf-8")
    if "scripts/backup_contabo.sh" not in text:
        raise AssertionError("deploy.yml must scp scripts/backup_contabo.sh to the VPS")
    if "/opt/arw-ml-lab/scripts/backup_contabo.sh" not in text:
        raise AssertionError("deploy.yml must place backup script under /opt/arw-ml-lab/scripts/")
    return {"id": ARTEFACT_ID, "seed": 42, "workflow": "deploy.yml"}
