"""GPU worker 422 guard — ARCHITECTURE §34.9 / Phase 2A (ST-ML-02 adjacent).

GPU-tagged catalogue entries refuse training when ``LAB_GPU_WORKER`` is not set;
API maps the guard ``ValueError`` to HTTP 422.
"""

from __future__ import annotations

from labcore.deep.guards import assert_gpu_allowed, gpu_worker_available
from labcore.registry.algorithms import thin_algorithm_specs

ARTEFACT_ID = "DEEP.GPU.GUARD"
HTTP_STATUS = 422
WORKER_ENV = "LAB_GPU_WORKER"


def gpu_only_algorithm_keys(*, include_tabpfn: bool = False) -> list[str]:
    """Registry keys with ``resources.gpu`` (TabPFN excluded unless requested)."""
    keys: list[str] = []
    for spec in thin_algorithm_specs():
        if not (spec.resources or {}).get("gpu"):
            continue
        if spec.enabled_env == "TABPFN_ENABLED" and not include_tabpfn:
            continue
        keys.append(spec.key)
    return sorted(keys)


def validate_train_gpu_guard(algorithm_keys: list[str]) -> None:
    """Raise ``ValueError`` (→ HTTP 422) when a GPU-only model has no worker."""
    by_key = {s.key: s for s in thin_algorithm_specs()}
    for key in algorithm_keys:
        spec = by_key.get(key)
        if spec is None:
            continue
        if spec.enabled_env == "TABPFN_ENABLED":
            continue
        assert_gpu_allowed(spec.resources)


def gpu_guard_manifest(*, seed: int = 42) -> dict[str, object]:
    return {
        "id": ARTEFACT_ID,
        "seed": seed,
        "http_status": HTTP_STATUS,
        "worker_env": WORKER_ENV,
        "worker_available": gpu_worker_available(),
        "gpu_only_keys": gpu_only_algorithm_keys(),
    }