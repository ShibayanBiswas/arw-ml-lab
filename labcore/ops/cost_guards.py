"""Workspace cost / concurrency guards — OPS-08 / ARCHITECTURE §25.

Offline-safe policy object. Contabo defaults match DEPLOY_CONTABO §12
(one heavy train at a time; AI daily caps when NVIDIA is configured).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

ARTEFACT_ID = "OPS.COST.GUARDS"
STRESS_ID = "ST-OPS-08"


@dataclass(frozen=True)
class CostGuardLimits:
    """Per-workspace soft limits (Contabo CPU box defaults)."""

    max_concurrent_jobs: int = 3
    max_concurrent_heavy: int = 1  # train/tune
    max_cpu_hours_per_day: float = 24.0
    max_storage_gb: float = 50.0
    max_ai_requests_per_day: int = 500
    seed: int = 42

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CostGuardUsage:
    concurrent_jobs: int = 0
    concurrent_heavy: int = 0
    cpu_hours_today: float = 0.0
    storage_gb: float = 0.0
    ai_requests_today: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_cost_guards(
    usage: CostGuardUsage,
    limits: CostGuardLimits | None = None,
) -> dict[str, Any]:
    """Return allow/deny with which limits are exceeded (never fabricates usage)."""
    limits = limits or CostGuardLimits()
    breaches: list[str] = []
    if usage.concurrent_jobs > limits.max_concurrent_jobs:
        breaches.append("max_concurrent_jobs")
    if usage.concurrent_heavy > limits.max_concurrent_heavy:
        breaches.append("max_concurrent_heavy")
    if usage.cpu_hours_today > limits.max_cpu_hours_per_day:
        breaches.append("max_cpu_hours_per_day")
    if usage.storage_gb > limits.max_storage_gb:
        breaches.append("max_storage_gb")
    if usage.ai_requests_today > limits.max_ai_requests_per_day:
        breaches.append("max_ai_requests_per_day")
    return {
        "id": ARTEFACT_ID,
        "stress_test": STRESS_ID,
        "seed": limits.seed,
        "allowed": len(breaches) == 0,
        "breaches": breaches,
        "limits": limits.to_dict(),
        "usage": usage.to_dict(),
    }


def guard_enqueue(
    *,
    concurrent_jobs: int,
    heavy: bool,
    concurrent_heavy: int = 0,
    limits: CostGuardLimits | None = None,
) -> dict[str, Any]:
    """Pre-enqueue check for light vs heavy Celery jobs."""
    limits = limits or CostGuardLimits()
    usage = CostGuardUsage(
        concurrent_jobs=concurrent_jobs + 1,
        concurrent_heavy=(concurrent_heavy + 1) if heavy else concurrent_heavy,
    )
    return evaluate_cost_guards(usage, limits)
