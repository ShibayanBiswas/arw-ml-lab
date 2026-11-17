"""Hold-out test set reuse log — MI-16 / ST-ML-04.

The final test split is locked after the first evaluation; each later evaluation
increments ``use_count`` and emits an audit row with action ``test.evaluation``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

ARTEFACT_ID = "MI.HOLDOUT.REUSE"
AUDIT_ACTION_HOLDOUT = "test.evaluation"
AUDIT_ENTITY = "run"


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


_GLOBAL_REGISTRY = HoldoutReuseRegistry()


def default_holdout_registry() -> HoldoutReuseRegistry:
    return _GLOBAL_REGISTRY