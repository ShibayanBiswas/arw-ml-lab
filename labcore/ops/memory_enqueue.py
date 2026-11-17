"""MI-09 / OPS memory guard before enqueue — ARCHITECTURE §39.3 + §46.1.

Contabo ``worker-train`` mem_limit is 3584 MiB (DEPLOY_CONTABO §5).
"""

from __future__ import annotations

import os
from typing import Any

from labcore.integrity.sample_size_policy import (
    estimate_training_memory_bytes,
    memory_enqueue_decision,
)

ARTEFACT_ID = "OPS.MEMORY.ENQUEUE"
STRESS_ID = "ST-ML-05"

# Contabo worker-train hard cap (bytes); overridable via env for other hosts.
DEFAULT_WORKER_TRAIN_LIMIT_BYTES = 3584 * 1024 * 1024


def worker_train_limit_bytes() -> int:
    raw = os.environ.get("LAB_WORKER_TRAIN_MEM_BYTES")
    if raw:
        return int(raw)
    return DEFAULT_WORKER_TRAIN_LIMIT_BYTES


def guard_train_enqueue(
    *,
    n_rows: int,
    n_cols: int,
    model_factor: float = 2.0,
    worker_limit_bytes: int | None = None,
) -> dict[str, Any]:
    """Return decision dict; caller raises HTTP 422 when ``refused``."""
    limit = worker_limit_bytes if worker_limit_bytes is not None else worker_train_limit_bytes()
    estimated = estimate_training_memory_bytes(n_rows, n_cols, model_factor=model_factor)
    decision = memory_enqueue_decision(estimated, limit)
    decision["artefact"] = ARTEFACT_ID
    decision["n_rows"] = int(n_rows)
    decision["n_cols"] = int(n_cols)
    return decision
