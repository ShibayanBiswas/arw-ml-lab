"""Admin workers & queues snapshot — OPS-12 (Flower-behind-admin alternative).

Offline-safe: accept an injectable ``inspect`` callable. Live Contabo uses Celery
``inspect().active()`` / ``reserved()`` / ``stats()`` when the broker is up.
"""

from __future__ import annotations

from typing import Any, Callable

ARTEFACT_ID = "OPS.ADMIN.WORKERS"
STRESS_ID = "ST-OPS-09"

# Contabo compose queue set (DEPLOY_CONTABO §5 / celery_app.QUEUES)
KNOWN_QUEUES: tuple[str, ...] = (
    "q.ingest",
    "q.eda",
    "q.train.cpu",
    "q.train.gpu",
    "q.tune",
    "q.explain",
    "q.forecast",
    "q.insights",
    "q.report",
    "q.predict.batch",
    "q.predict.heavy",
    "q.demo",
)


def empty_queue_depths() -> dict[str, int]:
    return {q: 0 for q in KNOWN_QUEUES}


def summarize_inspect(
    *,
    active: dict[str, list[Any]] | None = None,
    reserved: dict[str, list[Any]] | None = None,
    stats: dict[str, Any] | None = None,
    seed: int = 42,
) -> dict[str, Any]:
    """Build a JSON-safe workers/queues panel from Celery inspect payloads."""
    active = active or {}
    reserved = reserved or {}
    stats = stats or {}
    workers: list[dict[str, Any]] = []
    worker_names = sorted(set(active) | set(reserved) | set(stats))
    for name in worker_names:
        workers.append(
            {
                "name": name,
                "active": len(active.get(name) or []),
                "reserved": len(reserved.get(name) or []),
                "pool": (stats.get(name) or {}).get("pool"),
            }
        )
    depths = empty_queue_depths()
    # Best-effort: count active+reserved tasks by delivery_info.routing_key when present
    for bucket in (active, reserved):
        for tasks in bucket.values():
            for task in tasks or []:
                if not isinstance(task, dict):
                    continue
                delivery = task.get("delivery_info") or {}
                q = delivery.get("routing_key") or delivery.get("exchange")
                if isinstance(q, str) and q in depths:
                    depths[q] += 1
    return {
        "id": ARTEFACT_ID,
        "stress_test": STRESS_ID,
        "seed": seed,
        "flower_note": "Flower stays optional behind admin auth; this panel is the default Contabo view",
        "workers": workers,
        "queues": depths,
        "n_workers": len(workers),
        "broker_reachable": bool(worker_names),
    }


def collect_queue_stats(
    *,
    inspect_factory: Callable[[], Any] | None = None,
    seed: int = 42,
) -> dict[str, Any]:
    """Call Celery inspect when available; otherwise empty offline snapshot."""
    if inspect_factory is None:
        return summarize_inspect(seed=seed)
    try:
        insp = inspect_factory()
        if insp is None:
            return summarize_inspect(seed=seed)
        return summarize_inspect(
            active=insp.active() or {},
            reserved=insp.reserved() or {},
            stats=insp.stats() or {},
            seed=seed,
        )
    except Exception as exc:  # noqa: BLE001 — admin panel must never 500 on broker blip
        out = summarize_inspect(seed=seed)
        out["broker_reachable"] = False
        out["error"] = str(exc)
        return out
