"""Hold-out test set reuse log — MI-16 / ST-ML-04.

The final test split is locked after the first evaluation; each later evaluation
increments ``use_count`` and emits an audit row with action ``test.evaluation``.
Postgres ``audit_log`` insert is available via ``persist_holdout_audit_row`` (oneshot-c225).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

ARTEFACT_ID = "MI.HOLDOUT.REUSE"
AUDIT_ACTION_HOLDOUT = "test.evaluation"
AUDIT_ENTITY = "run"

_AUDIT_INSERT_SQL = """
INSERT INTO public.audit_log (workspace_id, action, entity, entity_id, detail)
VALUES (%s::uuid, %s, %s, %s, %s::jsonb)
RETURNING id
"""


@dataclass
class HoldoutReuseRegistry:
    """Process-local counter store (Postgres audit rows in hosted Phase 8.2)."""

    _counts: dict[str, int] = field(default_factory=dict)

    def fingerprint(self, *, dataset_id: str, test_size: float, seed: int) -> str:
        return f"{dataset_id}|test_size={test_size}|seed={seed}"


def build_holdout_audit_row(
    *,
    workspace_id: str,
    run_id: str,
    dataset_id: str,
    use_count: int,
    is_reuse: bool,
    seed: int,
) -> dict[str, Any]:
    return {
        "workspace_id": workspace_id,
        "action": AUDIT_ACTION_HOLDOUT,
        "entity": AUDIT_ENTITY,
        "entity_id": run_id,
        "detail": {
            "dataset_id": dataset_id,
            "split": "holdout",
            "use_count": use_count,
            "is_reuse": is_reuse,
            "seed": seed,
            "ui_label": f"test set used {use_count} time{'s' if use_count != 1 else ''}",
        },
    }


def log_holdout_test_use(
    registry: HoldoutReuseRegistry,
    *,
    workspace_id: str,
    run_id: str,
    dataset_id: str,
    test_size: float,
    seed: int = 42,
) -> dict[str, Any]:
    """Record one hold-out evaluation; returns manifest + suggested audit row."""
    key = registry.fingerprint(dataset_id=dataset_id, test_size=test_size, seed=seed)
    prior = registry._counts.get(key, 0)
    use_count = prior + 1
    registry._counts[key] = use_count
    is_reuse = prior > 0
    audit_row = build_holdout_audit_row(
        workspace_id=workspace_id,
        run_id=run_id,
        dataset_id=dataset_id,
        use_count=use_count,
        is_reuse=is_reuse,
        seed=seed,
    )
    return {
        "id": ARTEFACT_ID,
        "dataset_id": dataset_id,
        "test_size": test_size,
        "seed": seed,
        "use_count": use_count,
        "is_reuse": is_reuse,
        "locked_after_first_use": True,
        "audit_row": audit_row,
    }


def _is_uuid(value: object) -> bool:
    text = str(value or "").strip()
    if len(text) != 36:
        return False
    import re

    return bool(
        re.fullmatch(
            r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
            text,
        )
    )


def persist_holdout_audit_row(
    audit_row: dict[str, Any],
    *,
    execute: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    """Persist ``audit_row`` to ``public.audit_log`` when an executor is provided.

    ``execute`` should accept ``(sql, params)`` like ``psycopg.Connection.execute``.
    Without ``execute``, returns ``{"persisted": False}`` (offline / unit path).
    Skips when ``workspace_id`` is not a UUID (e.g. local ``offline``).
    """
    import json

    if execute is None:
        return {"persisted": False, "reason": "no_executor"}
    workspace_id = audit_row.get("workspace_id")
    if not _is_uuid(workspace_id):
        return {"persisted": False, "reason": "workspace_id_not_uuid"}
    detail = audit_row.get("detail") or {}
    cur = execute(
        _AUDIT_INSERT_SQL,
        (
            workspace_id,
            audit_row.get("action"),
            audit_row.get("entity"),
            audit_row.get("entity_id"),
            json.dumps(detail),
        ),
    )
    row_id = None
    try:
        fetched = cur.fetchone() if hasattr(cur, "fetchone") else None
        if fetched is not None:
            row_id = fetched[0] if not isinstance(fetched, dict) else fetched.get("id")
    except Exception:  # noqa: BLE001 — persistence must not break training
        row_id = None
    return {"persisted": True, "audit_id": row_id, "action": AUDIT_ACTION_HOLDOUT}


_GLOBAL_REGISTRY = HoldoutReuseRegistry()


def default_holdout_registry() -> HoldoutReuseRegistry:
    return _GLOBAL_REGISTRY