"""GPU / TabPFN guards (ARCHITECTURE §34.9, §39 TabPFN licence)."""

from __future__ import annotations

import os
from typing import Any


def tabpfn_enabled() -> bool:
    """TabPFN stays off unless admin sets TABPFN_ENABLED=true (licence)."""
    return os.environ.get("TABPFN_ENABLED", "false").strip().lower() in {"1", "true", "yes"}


def gpu_worker_available() -> bool:
    """True when a GPU Celery worker is registered (env LAB_GPU_WORKER=true)."""
    return os.environ.get("LAB_GPU_WORKER", "false").strip().lower() in {"1", "true", "yes"}


def assert_gpu_allowed(spec_resources: dict[str, Any] | None) -> None:
    """Raise ValueError (mapped to HTTP 422) if GPU-only and no GPU worker."""
    resources = spec_resources or {}
    if resources.get("gpu") and not gpu_worker_available():
        raise ValueError(
            "GPU worker required: no q.train.gpu worker is registered "
            "(set LAB_GPU_WORKER=true when a GPU worker is available). "
            "Try a CPU-capable model (e.g. dl.mlp / dl.tabnet) or a smaller preset."
        )
