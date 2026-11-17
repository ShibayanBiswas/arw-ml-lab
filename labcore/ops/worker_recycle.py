"""Worker recycle + graceful shutdown — OPS-02 / §39.3 / DEPLOY_CONTABO.

``worker_max_tasks_per_child=20`` and memory caps recycle leaky processes.
Compose ``stop_grace_period: 300s`` matches Render ``maxShutdownDelaySeconds: 300``.
Contabo train cap is lower than the 16 GB Render plan (8 GB host).
"""

from __future__ import annotations

from typing import Any

ARTEFACT_ID = "OPS.WORKER.RECYCLE"
STRESS_REF = "OPS-02"

# Celery ``worker_max_memory_per_child`` is in **kilobytes**.
MEMORY_PER_CHILD_KIB: dict[str, int] = {
    "worker-light": 1_400 * 1024,  # under compose mem_limit 1536m
    "worker-train": 3_200 * 1024,  # under Contabo mem_limit 3584m
}

MAX_TASKS_PER_CHILD = 20
STOP_GRACE_SECONDS = 300


def memory_per_child_kib(service_role: str) -> int:
    if service_role in MEMORY_PER_CHILD_KIB:
        return int(MEMORY_PER_CHILD_KIB[service_role])
    # Local/dev Celery and unknown roles inherit the Contabo light budget
    return int(MEMORY_PER_CHILD_KIB["worker-light"])


def celery_recycle_settings(service_role: str) -> dict[str, Any]:
    """Settings merged into Celery conf for the given SERVICE_ROLE."""
    kib = memory_per_child_kib(service_role)
    out: dict[str, Any] = {
        "worker_max_tasks_per_child": MAX_TASKS_PER_CHILD,
        "artefact": ARTEFACT_ID,
        "service_role": service_role,
        "stop_grace_seconds": STOP_GRACE_SECONDS,
    }
    if kib > 0:
        out["worker_max_memory_per_child"] = kib
    return out


def assert_worker_recycle_contract() -> dict[str, object]:
    light = celery_recycle_settings("worker-light")
    train = celery_recycle_settings("worker-train")
    if light["worker_max_tasks_per_child"] != MAX_TASKS_PER_CHILD:
        raise AssertionError("max_tasks_per_child must be 20")
    if light["worker_max_memory_per_child"] >= train["worker_max_memory_per_child"]:
        raise AssertionError("train memory cap must exceed light")
    if train["stop_grace_seconds"] != 300:
        raise AssertionError("stop_grace must be 300s")
    # Contabo train must stay under 3584 MiB compose limit
    train_mib = train["worker_max_memory_per_child"] / 1024
    if train_mib >= 3584:
        raise AssertionError("Contabo train max_memory must be < 3584 MiB")
    return {
        "id": ARTEFACT_ID,
        "light_mib": light["worker_max_memory_per_child"] / 1024,
        "train_mib": train_mib,
        "max_tasks": MAX_TASKS_PER_CHILD,
        "stop_grace_s": STOP_GRACE_SECONDS,
        "stress": STRESS_REF,
    }
