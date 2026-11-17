"""Offline restore-drill checklist — OPS-13 / ST-OPS-06 (oneshot-c198).

Hosted prove still requires Contabo + external rclone remote. This module
records the exact steps and verifies runbook coverage so the drill is
executable the moment secrets land.
"""

from __future__ import annotations

from typing import Any

from labcore.ops.storage_backup_contract import (
    ARTEFACT_ID as BACKUP_ARTEFACT,
    STORAGE_MIRROR_BUCKETS,
    assert_storage_backup_contract,
)

ARTEFACT_ID = "OPS.RESTORE.DRILL"
STRESS_ID = "ST-OPS-06"

DRILL_STEPS: tuple[dict[str, str], ...] = (
    {
        "id": "RD1",
        "action": "Confirm nightly rclone cron copied models/ and datasets/ off-site",
    },
    {
        "id": "RD2",
        "action": "Pick one model object key from the off-site mirror",
    },
    {
        "id": "RD3",
        "action": "rclone copy that object into a scratch prefix under /opt/arw-ml-lab/backups/drill/",
    },
    {
        "id": "RD4",
        "action": "Upload to a scratch Supabase Storage prefix; verify sha256 matches",
    },
    {
        "id": "RD5",
        "action": "Document outcome in docs/PHASE_8_1_REPORT.md restore drill section",
    },
)


def restore_drill_manifest(*, seed: int = 42, hosted_executed: bool = False) -> dict[str, Any]:
    backup_checks = assert_storage_backup_contract()
    return {
        "id": ARTEFACT_ID,
        "backup_artefact": BACKUP_ARTEFACT,
        "stress_id": STRESS_ID,
        "seed": seed,
        "buckets": list(STORAGE_MIRROR_BUCKETS),
        "steps": list(DRILL_STEPS),
        "backup_checks": backup_checks,
        "hosted_executed": hosted_executed,
        "status": "ready_offline" if not hosted_executed else "executed",
    }


def assert_restore_drill_ready() -> dict[str, object]:
    m = restore_drill_manifest(seed=42, hosted_executed=False)
    if len(m["steps"]) < 5:
        raise AssertionError("restore drill needs ≥5 steps")
    if m["status"] != "ready_offline":
        raise AssertionError("offline status expected until Contabo prove")
    return m
