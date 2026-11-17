"""Job reliability contract — heartbeat, reaper, idempotency (ST-OPS-03 / §46.2 OPS-03).

Offline scanner: migrations + worker kit paths must match the OPS-03 spec without
starting Celery, Redis, or Postgres.
"""

from __future__ import annotations

import re
from pathlib import Path

ARTEFACT_ID = "OPS.JOB.RELIABILITY"
HEARTBEAT_INTERVAL_S = 30
STALE_HEARTBEAT_S = 10 * 60


class JobReliabilityContractError(ValueError):
    """Raised when the kit violates ST-OPS-03 / OPS-03."""


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read(rel: str) -> str:
    path = _repo_root() / rel
    if not path.is_file():
        msg = f"missing kit file for OPS-03: {rel}"
        raise JobReliabilityContractError(msg)
    return path.read_text(encoding="utf-8")


def _require_substrings(text: str, needles: tuple[str, ...], label: str) -> None:
    missing = [n for n in needles if n not in text]
    if missing:
        raise JobReliabilityContractError(f"{label}: missing {missing!r}")


def assert_migration_ops03_schema() -> None:
    hardening = _read("supabase/migrations/20261115000100_hardening.sql")
    _require_substrings(
        hardening,
        (
            "heartbeat_at timestamptz",
            "idempotency_key text",
            "jobs_idem on public.jobs",
        ),
        "hardening migration",
    )
    prediction = _read("supabase/migrations/20261115000000_prediction_studio.sql")
    _require_substrings(
        prediction,
        (
            "prediction_jobs_idem on public.prediction_jobs",
            "idempotency_key text",
        ),
        "prediction_studio migration",
    )


def assert_celery_acks_late() -> None:
    celery_py = _read("backend/worker/celery_app.py")
    _require_substrings(
        celery_py,
        (
            "task_acks_late=True",
            "task_reject_on_worker_lost=True",
            "backend.worker import heartbeat",
        ),
        "celery_app",
    )


def assert_heartbeat_and_reaper_timing() -> None:
    hb = _read("backend/worker/heartbeat.py")
    match = re.search(r"^HEARTBEAT_INTERVAL_S\s*=\s*(\d+)", hb, re.MULTILINE)
    if not match or int(match.group(1)) != HEARTBEAT_INTERVAL_S:
        raise JobReliabilityContractError(
            f"heartbeat.py: HEARTBEAT_INTERVAL_S must be {HEARTBEAT_INTERVAL_S}"
        )
    maint = _read("backend/worker/maintenance.py")
    match_stale = re.search(r"^STALE_SECONDS\s*=\s*(\d+)\s*\*\s*60", maint, re.MULTILINE)
    if not match_stale or int(match_stale.group(1)) * 60 != STALE_HEARTBEAT_S:
        raise JobReliabilityContractError(
            f"maintenance.py: STALE_SECONDS must be {STALE_HEARTBEAT_S // 60} * 60"
        )


def assert_in_memory_idempotency_store() -> None:
    store = _read("backend/app/jobs_store.py")
    _require_substrings(
        store,
        (
            "_by_idempotency",
            "idempotency_key: str | None",
        ),
        "jobs_store",
    )


def assert_job_reliability_contract() -> dict[str, object]:
    """Run all OPS-03 offline checks; return a compact contract record."""
    assert_migration_ops03_schema()
    assert_celery_acks_late()
    assert_heartbeat_and_reaper_timing()
    assert_in_memory_idempotency_store()
    return {
        "heartbeat_interval_s": HEARTBEAT_INTERVAL_S,
        "stale_heartbeat_s": STALE_HEARTBEAT_S,
        "celery_acks_late": True,
        "celery_reject_on_worker_lost": True,
    }


def job_reliability_manifest(*, seed: int = 42) -> dict[str, object]:
    contract = assert_job_reliability_contract()
    return {
        "id": ARTEFACT_ID,
        "seed": seed,
        "stress_id": "ST-OPS-03",
        **contract,
    }