"""lab-beat hourly maintenance — ARCHITECTURE §39 / §46.2 OPS.

Phase 8.1: safe no-op stubs so Render cron does not crash.
Phase 8.2: heartbeats reaper, prediction retention, storage lifecycle.
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import UTC, datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("lab.maintenance")


STALE_SECONDS = 10 * 60  # 10 minutes without progress → failed
PREDICTION_RETENTION_SECONDS = 30 * 24 * 3600  # 30 days (§46 OPS-06)


def reaper_stale_heartbeats() -> dict[str, int]:
    """Mark queued/running jobs older than 10 min without progress as failed."""
    import time

    from backend.app.jobs_store import JOB_STORE

    now = time.time()
    marked = 0
    for job_id, rec in list(getattr(JOB_STORE, "_jobs", {}).items()):
        if rec.status not in ("queued", "running"):
            continue
        age = now - float(rec.created_at)
        if age >= STALE_SECONDS and float(rec.progress) < 1.0:
            JOB_STORE.update(
                job_id,
                status="error",
                error=f"stale heartbeat after {int(age)}s",
            )
            marked += 1
    log.info("reaper_stale_heartbeats: marked_failed=%s", marked)
    return {"marked_failed": marked}


def retention_expired_predictions() -> dict[str, int]:
    """Delete in-memory MODEL_STORE entries older than retention (when stamped)."""
    import time

    from backend.app.model_store import MODEL_STORE

    now = time.time()
    deleted = 0
    store = getattr(MODEL_STORE, "_models", None)
    if isinstance(store, dict):
        for mid, rec in list(store.items()):
            created = getattr(rec, "created_at", None)
            if created is None:
                continue
            if now - float(created) > PREDICTION_RETENTION_SECONDS:
                store.pop(mid, None)
                deleted += 1
    log.info("retention_expired_predictions: deleted=%s", deleted)
    return {"deleted": deleted}


def storage_lifecycle() -> dict[str, int]:
    """Count artefacts under local scratch (hosted storage sweep in 8.2-cont)."""
    from pathlib import Path

    scratch = Path("tmp") / "artefacts"
    touched = 0
    if scratch.exists():
        for p in scratch.rglob("*"):
            if p.is_file():
                touched += 1
    log.info("storage_lifecycle: touched=%s", touched)
    return {"touched": touched}


def run_all() -> dict[str, object]:
    started = datetime.now(UTC).isoformat()
    result = {
        "started_at": started,
        "reaper": reaper_stale_heartbeats(),
        "predictions": retention_expired_predictions(),
        "storage": storage_lifecycle(),
        "seed": 42,
    }
    log.info("maintenance complete: %s", result)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ARW ML Lab maintenance (lab-beat)")
    parser.add_argument("--all", action="store_true", help="Run all maintenance tasks")
    parser.add_argument("--reaper", action="store_true", help="Stale-heartbeat reaper only")
    parser.add_argument("--predictions", action="store_true", help="Prediction retention only")
    parser.add_argument("--storage", action="store_true", help="Storage lifecycle only")
    args = parser.parse_args(argv)

    if args.all or not any((args.reaper, args.predictions, args.storage)):
        run_all()
        return 0
    if args.reaper:
        reaper_stale_heartbeats()
    if args.predictions:
        retention_expired_predictions()
    if args.storage:
        storage_lifecycle()
    return 0


if __name__ == "__main__":
    sys.exit(main())
