"""Soft time-limit → best-so-far persistence — OPS-03 / ARCHITECTURE §39.3.

Celery raises ``SoftTimeLimitExceeded`` at the soft limit. Tasks should catch it,
persist whatever partial result exists, and return a truncated payload instead of
losing the run. Hard limit still kills the process.

Mid-run: train/tune pass a ``PartialHolder`` into CV/Optuna callbacks so a soft
kill mid-loop still has completed algorithms/trials, not an empty ``partial``.
"""

from __future__ import annotations

from typing import Any

ARTEFACT_ID = "OPS.SOFT.TIME_LIMIT"
STRESS_ID = "ST-OPS-03"


class PartialHolder:
    """Mutable best-so-far bag shared by the task body and mid-run callbacks."""

    __slots__ = ("value",)

    def __init__(self, initial: dict[str, Any] | None = None) -> None:
        self.value: dict[str, Any] | None = dict(initial) if initial else None

    def update(self, snapshot: dict[str, Any]) -> None:
        """Replace the held partial with a JSON-safe snapshot (no pipelines)."""
        self.value = dict(snapshot)


def sanitize_leaderboard_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Drop private ``_pipeline`` / ``_oof`` keys before persisting best-so-far."""
    clean: list[dict[str, Any]] = []
    for row in rows:
        clean.append({k: v for k, v in row.items() if not str(k).startswith("_")})
    return clean


def truncated_result(
    partial: dict[str, Any] | None,
    *,
    reason: str = "soft_time_limit",
    seed: int = 42,
) -> dict[str, Any]:
    """Wrap a partial payload so UIs can show best-so-far after a soft limit."""
    body = dict(partial or {})
    body["truncated"] = True
    body["truncation_reason"] = reason
    body["seed"] = seed
    body["artefact"] = ARTEFACT_ID
    return body


def is_soft_time_limit_exc(exc: BaseException) -> bool:
    """True for Celery SoftTimeLimitExceeded without importing billiard at module load."""
    name = type(exc).__name__
    if name == "SoftTimeLimitExceeded":
        return True
    # billiard.exceptions.SoftTimeLimitExceeded
    mod = type(exc).__module__ or ""
    return "SoftTimeLimitExceeded" in name and ("billiard" in mod or "celery" in mod)


def save_best_so_far(
    *,
    job_update: Any,
    experiment_update: Any | None = None,
    job_id: str,
    experiment_id: str | None,
    partial: dict[str, Any] | None,
    seed: int = 42,
) -> dict[str, Any]:
    """Persist truncated result via injectable store updaters (testable offline)."""
    result = truncated_result(partial, seed=seed)
    job_update(
        job_id,
        status="done",
        progress=1.0,
        step="soft_time_limit",
        result=result,
        event={"type": "done", "truncated": True, "reason": "soft_time_limit"},
    )
    if experiment_update is not None and experiment_id:
        experiment_update(
            experiment_id,
            status="done",
            leaderboard=list(result.get("leaderboard") or []),
            result=result,
        )
    return result
