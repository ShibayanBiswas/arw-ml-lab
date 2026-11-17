"""Predict batch Idempotency-Key reuse — §45.8 / oneshot-c250."""

from __future__ import annotations

from pathlib import Path
from typing import Any

ARTEFACT_ID = "PRED.BATCH.IDEMPOTENCY"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def assert_predict_batch_idempotency_wiring(
    *,
    router_path: Path | None = None,
    store_path: Path | None = None,
) -> dict[str, Any]:
    """Router must accept Idempotency-Key and JobStore must reuse keys."""
    root = _repo_root()
    router = (router_path or root / "backend" / "app" / "routers" / "predict.py").read_text(
        encoding="utf-8"
    )
    store = (store_path or root / "backend" / "app" / "jobs_store.py").read_text(encoding="utf-8")
    errors: list[str] = []
    if 'alias="Idempotency-Key"' not in router and "Idempotency-Key" not in router:
        errors.append("predict router must accept Idempotency-Key header")
    if "idempotency_key=idempotency_key" not in router and "idempotency_key=" not in router:
        errors.append("predict router must pass idempotency_key into JOB_STORE.create")
    if "_by_idempotency" not in store:
        errors.append("JobStore must index by idempotency key")
    if "if idempotency_key and idempotency_key in self._by_idempotency" not in store:
        errors.append("JobStore.create must return existing job for same key")
    if errors:
        raise AssertionError(f"{ARTEFACT_ID}: " + "; ".join(errors))
    return {"id": ARTEFACT_ID, "seed": 42, "checks": 3}


def assert_job_store_idempotency_runtime(*, seed: int = 42) -> dict[str, Any]:
    from backend.app.jobs_store import JobStore

    store = JobStore()
    a = store.create(idempotency_key="batch-key-1")
    b = store.create(idempotency_key="batch-key-1")
    c = store.create(idempotency_key="batch-key-2")
    if a.job_id != b.job_id:
        raise AssertionError(f"{ARTEFACT_ID}: same key must reuse job_id")
    if a.job_id == c.job_id:
        raise AssertionError(f"{ARTEFACT_ID}: different keys must differ")
    return {"id": ARTEFACT_ID, "seed": seed, "reuse": True, "distinct": True}
