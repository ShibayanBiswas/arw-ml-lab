"""Deep learning thin slice (Phase 2A) — Lightning + pytorch-tabular + sequential windows."""

from __future__ import annotations

from labcore.deep.gpu_guard_contract import (
    ARTEFACT_ID as GPU_GUARD_ARTEFACT_ID,
    gpu_guard_manifest,
    validate_train_gpu_guard,
)
from labcore.deep.guards import (
    assert_gpu_allowed,
    gpu_worker_available,
    tabpfn_enabled,
)
from labcore.deep.registry import deep_algorithm_specs

__all__ = [
    "GPU_GUARD_ARTEFACT_ID",
    "assert_gpu_allowed",
    "deep_algorithm_specs",
    "gpu_guard_manifest",
    "gpu_worker_available",
    "tabpfn_enabled",
    "validate_train_gpu_guard",
]
