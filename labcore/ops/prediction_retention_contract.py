"""Prediction retention contract (ST-OPS-07 / §45.8 / §46.2).

Offline scanner: migrations + maintenance must enforce 30-day job expiry,
Storage purge before row delete, and a 1 000-row cap on ``prediction_results``.
"""

from __future__ import annotations

import re
from pathlib import Path

ARTEFACT_ID = "OPS.PREDICTION.RETENTION"
PREDICTION_RETENTION_DAYS = 30
PREDICTION_RESULTS_CAP = 1000
MAINTENANCE_MODULE = "backend.worker.maintenance"


class PredictionRetentionContractError(ValueError):
    """Raised when the kit violates ST-OPS-07."""


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read(rel: str) -> str:
    path = _repo_root() / rel
    if not path.is_file():
        msg = f"missing kit file for ST-OPS-07: {rel}"
        raise PredictionRetentionContractError(msg)
    return path.read_text(encoding="utf-8")


def _require_substrings(text: str, needles: tuple[str, ...], label: str) -> None:
    missing = [n for n in needles if n not in text]
    if missing:
        raise PredictionRetentionContractError(f"{label}: missing {missing!r}")


def assert_prediction_migration_expires_at() -> dict[str, int | str]:
    sql = _read("supabase/migrations/20261115000000_prediction_studio.sql")
    _require_substrings(
        sql,
        (
            "expires_at timestamptz not null",
            "interval '30 days'",
            "first 1 000 rows",
        ),
        "prediction_studio migration",
    )
    return {"migration": "20261115000000_prediction_studio.sql", "retention_days": PREDICTION_RETENTION_DAYS}


def assert_hardening_expired_prediction_jobs() -> dict[str, str]:
    sql = _read("supabase/migrations/20261115000100_hardening.sql")
    if "ST-OPS-07" not in sql:
        raise PredictionRetentionContractError(
            "hardening migration: missing ST-OPS-07 retention comment",
        )
    if not re.search(
        r"create or replace function public\.expired_prediction_jobs\(\)",
        sql,
        re.IGNORECASE,
    ):
        raise PredictionRetentionContractError(
            "hardening migration: missing expired_prediction_jobs()",
        )
    return {"function": "expired_prediction_jobs"}


def assert_maintenance_prediction_retention() -> dict[str, int | str]:
    maint = _read("backend/worker/maintenance.py")
    _require_substrings(
        maint,
        (
            "ST-OPS-07",
            "purge_prediction_storage",
            "_EXPIRED_PREDICTION_PATHS_SQL",
            "_RETENTION_SQL",
            "_TRIM_PREDICTION_RESULTS_SQL",
            '"predictions": retention_expired_predictions()',
        ),
        "maintenance.py",
    )
    cap_match = re.search(r"^PREDICTION_RESULTS_CAP\s*=\s*(\d+)", maint, re.MULTILINE)
    if not cap_match or int(cap_match.group(1)) != PREDICTION_RESULTS_CAP:
        raise PredictionRetentionContractError(
            f"maintenance.py: PREDICTION_RESULTS_CAP must be {PREDICTION_RESULTS_CAP}",
        )
    retention_match = re.search(
        r"^PREDICTION_RETENTION_SECONDS\s*=\s*30\s*\*\s*24\s*\*\s*3600",
        maint,
        re.MULTILINE,
    )
    if not retention_match:
        raise PredictionRetentionContractError(
            "maintenance.py: PREDICTION_RETENTION_SECONDS must be 30 * 24 * 3600",
        )
    if "purge_prediction_storage(keys)" not in maint:
        raise PredictionRetentionContractError(
            "maintenance.py: must purge Storage before deleting expired rows",
        )
    return {
        "module": MAINTENANCE_MODULE,
        "results_cap": PREDICTION_RESULTS_CAP,
        "retention_days": PREDICTION_RETENTION_DAYS,
    }


def assert_prediction_retention_contract() -> dict[str, object]:
    """Run all ST-OPS-07 offline checks."""
    mig = assert_prediction_migration_expires_at()
    fn = assert_hardening_expired_prediction_jobs()
    worker = assert_maintenance_prediction_retention()
    return {
        "expires_at": mig,
        "expired_fn": fn,
        "maintenance": worker,
    }


def prediction_retention_manifest(*, seed: int = 42) -> dict[str, object]:
    contract = assert_prediction_retention_contract()
    return {
        "id": ARTEFACT_ID,
        "seed": seed,
        "stress_id": "ST-OPS-07",
        **contract,
    }