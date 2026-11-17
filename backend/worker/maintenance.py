"""lab-beat hourly maintenance — ARCHITECTURE §39 / §46.2 OPS.

Heartbeats reaper (OPS-03), prediction retention (OPS-07 / ST-OPS-07), and
storage lifecycle hooks (OPS-06). Uses Postgres when ``DATABASE_URL`` is
reachable; otherwise falls back to in-memory stores for local dev/tests.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import TYPE_CHECKING

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("lab.maintenance")

if TYPE_CHECKING:
    from collections.abc import Sequence

PREDICTIONS_BUCKET = "predictions"

STALE_SECONDS = 10 * 60  # 10 minutes without heartbeat → failed (§46.2 OPS-03)
PREDICTION_RETENTION_SECONDS = 30 * 24 * 3600  # 30 days (§46 OPS-06 / §45.8)
PREDICTION_RESULTS_CAP = 1000
MAINTENANCE_SEED = 42

_REAPER_SQL = """
UPDATE public.jobs
SET status = 'failed',
    error = coalesce(
        nullif(trim(error), ''),
        '[maintenance] stale heartbeat (no progress for 10 minutes)'
    ),
    finished_at = coalesce(finished_at, now())
WHERE status IN ('queued', 'running')
  AND (
    (heartbeat_at IS NOT NULL AND heartbeat_at < now() - make_interval(secs => %s))
    OR (
      heartbeat_at IS NULL
      AND coalesce(started_at, created_at) < now() - make_interval(secs => %s)
    )
  )
RETURNING id::text;
"""

_EXPIRED_PREDICTION_PATHS_SQL = """
SELECT input_path, output_path
FROM public.prediction_jobs
WHERE expires_at < now();
"""

_RETENTION_SQL = """
DELETE FROM public.prediction_jobs
WHERE expires_at < now()
RETURNING id::text;
"""

_TRIM_PREDICTION_RESULTS_SQL = """
DELETE FROM public.prediction_results
WHERE id IN (
  SELECT id FROM (
    SELECT id,
           row_number() OVER (PARTITION BY prediction_job_id ORDER BY id) AS rn
    FROM public.prediction_results
  ) ranked
  WHERE rn > %s
)
RETURNING id;
"""


def _connect_postgres():
    """Return a psycopg connection or None when the database is unavailable."""
    try:
        import psycopg

        from backend.app.settings import get_settings

        settings = get_settings()
        # Prefer session/direct URL for long maintenance transactions (§39)
        dsn = settings.database_url_session or settings.database_url
        conn = psycopg.connect(dsn, connect_timeout=5)
        conn.autocommit = True
        return conn
    except Exception as exc:  # noqa: BLE001 — maintenance must not crash on connect errors
        log.warning("postgres maintenance skipped: %s", exc)
        return None


@contextmanager
def _postgres() -> Iterator[object | None]:
    conn = _connect_postgres()
    try:
        yield conn
    finally:
        if conn is not None:
            conn.close()


def reaper_stale_heartbeats_postgres(conn: object) -> dict[str, int | str]:
    with conn.cursor() as cur:  # type: ignore[attr-defined]
        cur.execute(_REAPER_SQL, (STALE_SECONDS, STALE_SECONDS))
        marked = len(cur.fetchall())
    log.info("reaper_stale_heartbeats_postgres: marked_failed=%s", marked)
    return {"marked_failed": marked, "backend": "postgres"}


def reaper_stale_heartbeats_memory() -> dict[str, int | str]:
    """Mark queued/running in-memory demo jobs with stale heartbeats as failed."""
    from backend.app.jobs_store import JOB_STORE

    now = time.time()
    marked = 0
    for job_id, rec in list(getattr(JOB_STORE, "_jobs", {}).items()):
        if rec.status not in ("queued", "running"):
            continue
        last = getattr(rec, "heartbeat_at", None)
        stale_for = now - float(last) if last is not None else now - float(rec.created_at)
        if stale_for >= STALE_SECONDS and float(rec.progress) < 1.0:
            JOB_STORE.update(
                job_id,
                status="error",
                error=f"stale heartbeat after {int(stale_for)}s",
            )
            marked += 1
    log.info("reaper_stale_heartbeats_memory: marked_failed=%s", marked)
    return {"marked_failed": marked, "backend": "memory"}


def reaper_stale_heartbeats() -> dict[str, int | str]:
    with _postgres() as conn:
        if conn is not None:
            return reaper_stale_heartbeats_postgres(conn)
    return reaper_stale_heartbeats_memory()


def normalize_prediction_storage_key(path: str | None) -> str | None:
    """Strip bucket prefix so keys work with ``storage.from_('predictions')``."""
    if path is None:
        return None
    raw = str(path).strip()
    if not raw:
        return None
    p = raw.lstrip("/")
    prefix = f"{PREDICTIONS_BUCKET}/"
    if p.startswith(prefix):
        p = p[len(prefix) :]
    return p


def collect_prediction_storage_keys(
    rows: list[tuple[str | None, str | None]],
) -> list[str]:
    keys: list[str] = []
    seen: set[str] = set()
    for input_path, output_path in rows:
        for raw in (input_path, output_path):
            key = normalize_prediction_storage_key(raw)
            if key is not None and key not in seen:
                seen.add(key)
                keys.append(key)
    return keys


def purge_prediction_storage_local(keys: list[str]) -> int:
    """Remove dev copies under ``.cache/uploads`` when present."""
    from backend.app.storage import LOCAL_ROOT

    removed = 0
    for key in keys:
        path = LOCAL_ROOT / key
        if path.is_file():
            path.unlink(missing_ok=True)
            removed += 1
    return removed


def purge_prediction_storage_supabase(keys: list[str]) -> int:
    """Delete objects from the hosted ``predictions`` bucket (service role)."""
    try:
        from supabase import create_client

        from backend.app.settings import get_settings

        settings = get_settings()
        if not settings.supabase_service_role_key or "127.0.0.1" in settings.supabase_url:
            return 0
        client = create_client(settings.supabase_url, settings.supabase_service_role_key)
        # Supabase client accepts up to ~100 keys per remove call; batch conservatively.
        removed = 0
        chunk = 50
        for i in range(0, len(keys), chunk):
            batch = keys[i : i + chunk]
            resp = client.storage.from_(PREDICTIONS_BUCKET).remove(batch)
            if isinstance(resp, list):
                removed += len(resp)
            else:
                removed += len(batch)
        return removed
    except Exception as exc:  # noqa: BLE001 — retention must continue if Storage is down
        log.warning("prediction storage purge skipped: %s", exc)
        return 0


def purge_prediction_storage(keys: list[str]) -> dict[str, int | str]:
    if not keys:
        return {"storage_removed": 0, "storage_backend": "none"}
    supa = purge_prediction_storage_supabase(keys)
    local = purge_prediction_storage_local(keys)
    removed = max(supa, local) if supa or local else 0
    backend = "supabase" if supa else "local" if local else "none"
    log.info(
        "purge_prediction_storage: keys=%s removed=%s backend=%s",
        len(keys),
        removed,
        backend,
    )
    return {"storage_removed": removed, "storage_backend": backend, "storage_keys": len(keys)}


def retention_expired_predictions_postgres(conn: object) -> dict[str, int | str]:
    with conn.cursor() as cur:  # type: ignore[attr-defined]
        cur.execute(_EXPIRED_PREDICTION_PATHS_SQL)
        path_rows = cur.fetchall()
        keys = collect_prediction_storage_keys(path_rows)
        storage_stats = purge_prediction_storage(keys)
        cur.execute(_RETENTION_SQL)
        deleted = len(cur.fetchall())
    log.info("retention_expired_predictions_postgres: deleted=%s", deleted)
    return {
        "deleted": deleted,
        "backend": "postgres",
        **storage_stats,
    }


def retention_expired_predictions_memory() -> dict[str, int | str]:
    """Purge aged in-memory model entries (local predict demo only)."""
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
    log.info("retention_expired_predictions_memory: deleted=%s", deleted)
    return {"deleted": deleted, "backend": "memory"}


def retention_expired_predictions() -> dict[str, int | str]:
    with _postgres() as conn:
        if conn is not None:
            return retention_expired_predictions_postgres(conn)
    return retention_expired_predictions_memory()


def storage_lifecycle_postgres(conn: object) -> dict[str, int | str]:
    with conn.cursor() as cur:  # type: ignore[attr-defined]
        cur.execute(_TRIM_PREDICTION_RESULTS_SQL, (PREDICTION_RESULTS_CAP,))
        trimmed = len(cur.fetchall())
    log.info("storage_lifecycle_postgres: prediction_results_trimmed=%s", trimmed)
    return {"prediction_results_trimmed": trimmed, "backend": "postgres"}


def storage_lifecycle_scratch() -> int:
    """Count artefact scratch files (hosted Storage purge is worker-side)."""
    from pathlib import Path

    scratch = Path("tmp") / "artefacts"
    touched = 0
    if scratch.exists():
        for p in scratch.rglob("*"):
            if p.is_file():
                touched += 1
    return touched


def storage_lifecycle() -> dict[str, int | str]:
    trimmed = 0
    backend = "scratch"
    with _postgres() as conn:
        if conn is not None:
            stats = storage_lifecycle_postgres(conn)
            trimmed = int(stats["prediction_results_trimmed"])
            backend = str(stats["backend"])
    touched = storage_lifecycle_scratch()
    log.info("storage_lifecycle: prediction_results_trimmed=%s scratch_files=%s", trimmed, touched)
    return {
        "prediction_results_trimmed": trimmed,
        "scratch_files": touched,
        "backend": backend,
    }


def ping_healthcheck() -> dict[str, str | bool]:
    """Optional external heartbeat — DEPLOY_CONTABO §11 HEALTHCHECK_PING_URL."""
    url = (os.environ.get("HEALTHCHECK_PING_URL") or "").strip()
    if not url:
        return {"configured": False, "ok": True, "reason": "unset"}
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:  # noqa: S310 — operator-configured URL
            status = int(getattr(resp, "status", 0) or 0)
        ok = 200 <= status < 300
        if not ok:
            log.warning("healthcheck ping returned status=%s", status)
        return {"configured": True, "ok": ok, "status": status}
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        log.warning("healthcheck ping failed: %s", exc)
        return {"configured": True, "ok": False, "reason": type(exc).__name__}


def run_all() -> dict[str, object]:
    started = datetime.now(UTC).isoformat()
    result = {
        "started_at": started,
        "reaper": reaper_stale_heartbeats(),
        "predictions": retention_expired_predictions(),
        "storage": storage_lifecycle(),
        "healthcheck": ping_healthcheck(),
        "seed": MAINTENANCE_SEED,
    }
    log.info("maintenance complete: %s", result)
    return result


def main(argv: Sequence[str] | None = None) -> int:
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