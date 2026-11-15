"""Deep learning thin slice (Phase 2A) — Lightning + pytorch-tabular + sequential windows."""

from __future__ import annotations

from labcore.deep.guards import (
    assert_gpu_allowed,
    gpu_worker_available,
    tabpfn_enabled,
)
from labcore.deep.registry import deep_algorithm_specs

__all__ = [
    "assert_gpu_allowed",
    "deep_algorithm_specs",
    "gpu_worker_available",
    "tabpfn_enabled",
]
