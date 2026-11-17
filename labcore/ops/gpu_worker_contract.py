"""GPU worker refusal contract (DEPLOY_CONTABO §12 / ARCHITECTURE §34.9).

Contabo and default compose set ``LAB_GPU_WORKER=false``. Train and tune routes
must return HTTP 422 when a GPU-only algorithm is requested and no GPU worker is
registered (``labcore.deep.guards.assert_gpu_allowed``).
"""

from __future__ import annotations

import re
from pathlib import Path

ARTEFACT_ID = "OPS.GPU.WORKER"
ENV_LAB_GPU_WORKER = "LAB_GPU_WORKER"
DEFAULT_LAB_GPU_WORKER = "false"
HTTP_STATUS_GPU_REFUSED = 422
CONTABO_DOC = "docs/DEPLOY_CONTABO.md"
COMPOSE_PROD = "docker-compose.prod.yml"
EXPERIMENTS_ROUTER = "backend/app/routers/experiments.py"


class GpuWorkerContractError(ValueError):
    """Raised when the kit violates the Contabo §12 GPU refusal contract."""


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read(rel: str) -> str:
    path = _repo_root() / rel
    if not path.is_file():
        msg = f"missing kit file for {ARTEFACT_ID}: {rel}"
        raise GpuWorkerContractError(msg)
    return path.read_text(encoding="utf-8")


def gpu_only_algorithm_keys() -> list[str]:
    """Registry keys with ``resources.gpu=true`` (visible or catalogue-only)."""
    from labcore.registry.algorithms import thin_algorithm_specs

    return sorted(
        s.key
        for s in thin_algorithm_specs()
        if (s.resources or {}).get("gpu") is True
    )


def assert_compose_lab_gpu_worker_false(compose_path: Path | None = None) -> dict[str, str]:
    """``docker-compose.prod.yml`` must default ``LAB_GPU_WORKER`` to false on train worker."""
    path = compose_path or (_repo_root() / COMPOSE_PROD)
    if not path.is_file():
        msg = f"{COMPOSE_PROD} missing: {path}"
        raise GpuWorkerContractError(msg)
    text = path.read_text(encoding="utf-8")
    if "worker-train:" not in text:
        raise GpuWorkerContractError(f"{COMPOSE_PROD}: missing worker-train service")
    block = text.split("worker-train:", 1)[1]
    if "LAB_GPU_WORKER" not in block:
        raise GpuWorkerContractError(f"{COMPOSE_PROD}: worker-train missing LAB_GPU_WORKER")
    if not re.search(
        r'LAB_GPU_WORKER:\s*["\']?false["\']?',
        block,
        re.IGNORECASE,
    ):
        raise GpuWorkerContractError(
            f"{COMPOSE_PROD}: worker-train LAB_GPU_WORKER must be false (Contabo §12)",
        )
    return {
        "compose": path.name,
        ENV_LAB_GPU_WORKER: DEFAULT_LAB_GPU_WORKER,
    }


def assert_deploy_contabo_section12_gpu_422(doc_path: Path | None = None) -> dict[str, str]:
    """DEPLOY_CONTABO §12 documents HTTP 422 refusal when no GPU worker."""
    path = doc_path or (_repo_root() / CONTABO_DOC)
    if not path.is_file():
        msg = f"{CONTABO_DOC} missing: {path}"
        raise GpuWorkerContractError(msg)
    text = path.read_text(encoding="utf-8")
    if not re.search(r"##\s+12\.\s+Operations", text):
        raise GpuWorkerContractError(f"{CONTABO_DOC}: missing §12 Operations")
    section = text.split("## 12. Operations", 1)[-1].split("## 13.", 1)[0]
    needles = ("LAB_GPU_WORKER=false", "HTTP 422", "GPU models")
    missing = [n for n in needles if n not in section]
    if missing:
        raise GpuWorkerContractError(f"{CONTABO_DOC} §12: missing {missing!r}")
    return {"doc": path.name, "section": "12", "http_status": str(HTTP_STATUS_GPU_REFUSED)}


def assert_experiments_router_maps_gpu_to_422(
    router_path: Path | None = None,
) -> dict[str, str]:
    """Train/tune router must call ``assert_gpu_allowed`` and map failures to HTTP 422."""
    path = router_path or (_repo_root() / EXPERIMENTS_ROUTER)
    if not path.is_file():
        msg = f"{EXPERIMENTS_ROUTER} missing: {path}"
        raise GpuWorkerContractError(msg)
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if "assert_gpu_allowed" not in text and "validate_train_gpu_guard" not in text:
        errors.append(
            f"{EXPERIMENTS_ROUTER}: must call assert_gpu_allowed or validate_train_gpu_guard",
        )
    if "status_code=422" not in text:
        errors.append(f"{EXPERIMENTS_ROUTER}: must raise HTTPException with status_code=422")
    if errors:
        raise GpuWorkerContractError("; ".join(errors))
    return {"router": path.name, "http_status": str(HTTP_STATUS_GPU_REFUSED)}


def assert_gpu_worker_contract(
    *,
    compose_path: Path | None = None,
    doc_path: Path | None = None,
    router_path: Path | None = None,
) -> list[dict[str, str]]:
    """Run all offline checks for Contabo §12 GPU refusal."""
    checks = [
        assert_compose_lab_gpu_worker_false(compose_path),
        assert_deploy_contabo_section12_gpu_422(doc_path),
        assert_experiments_router_maps_gpu_to_422(router_path),
    ]
    keys = gpu_only_algorithm_keys()
    if "seq.xlstm" not in keys:
        raise GpuWorkerContractError(
            "registry: expected seq.xlstm (Q12) in gpu_only_algorithm_keys",
        )
    checks.append(
        {
            "registry": "gpu_only_algorithm_keys",
            "count": str(len(keys)),
            "keys": ",".join(keys),
        },
    )
    return checks


def gpu_worker_manifest(*, seed: int = 42) -> dict[str, object]:
    checks = assert_gpu_worker_contract()
    return {
        "id": ARTEFACT_ID,
        "seed": seed,
        ENV_LAB_GPU_WORKER: DEFAULT_LAB_GPU_WORKER,
        "http_status_gpu_refused": HTTP_STATUS_GPU_REFUSED,
        "gpu_only_algorithm_keys": gpu_only_algorithm_keys(),
        "checks": checks,
    }