"""Offline artefact OPS.CONTABO.LIMITS — DEPLOY_CONTABO §5 / §12.

Scans docker-compose.prod.yml for the 8 GB VPS budget: worker-train
concurrency 1, memory caps, LAB_GPU_WORKER=false, redis not published.
"""

from __future__ import annotations

from pathlib import Path

import yaml

ARTEFACT_ID = "OPS.CONTABO.LIMITS"
STRESS_ID = "ST-OPS-11"

ROOT = Path(__file__).resolve().parents[2]
COMPOSE = ROOT / "docker-compose.prod.yml"
DEPLOY_DOC = ROOT / "docs" / "DEPLOY_CONTABO.md"


class ContaboLimitsContractError(ValueError):
    """Raised when Contabo VPS limit markers are wrong."""


def _load_compose() -> dict:
    raw = COMPOSE.read_text(encoding="utf-8")
    data = yaml.safe_load(raw)
    if not isinstance(data, dict) or "services" not in data:
        raise ContaboLimitsContractError("compose missing services")
    return data


def assert_worker_train_one_heavy() -> dict[str, object]:
    svc = _load_compose()["services"]["worker-train"]
    cmd = svc.get("command") or []
    if not isinstance(cmd, list):
        raise ContaboLimitsContractError("worker-train command must be a list")
    joined = " ".join(str(c) for c in cmd)
    if "--concurrency" not in joined:
        raise ContaboLimitsContractError("worker-train missing --concurrency")
    # find value after --concurrency
    try:
        idx = [str(c) for c in cmd].index("--concurrency")
        conc = str(cmd[idx + 1]).strip('"')
    except (ValueError, IndexError) as exc:
        raise ContaboLimitsContractError("cannot parse --concurrency") from exc
    if conc != "1":
        raise ContaboLimitsContractError(f"worker-train concurrency must be 1, got {conc}")
    env = svc.get("environment") or {}
    if str(env.get("LAB_GPU_WORKER", "")).lower() not in {"false", "0"}:
        raise ContaboLimitsContractError("LAB_GPU_WORKER must be false on worker-train")
    mem = str(svc.get("mem_limit", ""))
    if mem not in {"3584m", "3.5g", "3584M"}:
        # allow 3584m as in compose
        if "3584" not in mem and "3.5" not in mem.lower():
            raise ContaboLimitsContractError(f"worker-train mem_limit unexpected: {mem}")
    return {
        "concurrency": 1,
        "lab_gpu_worker": env.get("LAB_GPU_WORKER"),
        "mem_limit": mem,
    }


def assert_redis_not_published() -> dict[str, object]:
    redis = _load_compose()["services"]["redis"]
    if redis.get("ports"):
        raise ContaboLimitsContractError("redis must not publish ports")
    cmd = redis.get("command") or []
    joined = " ".join(str(c) for c in cmd) if isinstance(cmd, list) else str(cmd)
    if "requirepass" not in joined and "${REDIS_PASSWORD" not in joined:
        # compose may use shell form
        if "requirepass" not in str(redis):
            raise ContaboLimitsContractError("redis must require a password")
    return {"ports_published": False, "auth": True}


def assert_only_caddy_publishes() -> dict[str, object]:
    services = _load_compose()["services"]
    published = {name: svc.get("ports") for name, svc in services.items() if svc.get("ports")}
    if set(published) != {"caddy"}:
        raise ContaboLimitsContractError(f"only caddy may publish ports; got {published}")
    return {"published_services": sorted(published)}


def assert_deploy_doc_section_12() -> dict[str, object]:
    text = DEPLOY_DOC.read_text(encoding="utf-8")
    needles = (
        "Concurrent heavy jobs",
        "LAB_GPU_WORKER=false",
        "HTTP 422",
        "concurrency 1",
        "8 GB",
    )
    missing = [n for n in needles if n not in text]
    if missing:
        raise ContaboLimitsContractError(f"DEPLOY_CONTABO missing {missing}")
    return {"doc_ok": True}


def assert_contabo_limits_contract() -> list[dict[str, object]]:
    return [
        assert_worker_train_one_heavy(),
        assert_redis_not_published(),
        assert_only_caddy_publishes(),
        assert_deploy_doc_section_12(),
    ]


def contabo_limits_manifest(*, seed: int = 42) -> dict[str, object]:
    return {
        "id": ARTEFACT_ID,
        "stress_test": STRESS_ID,
        "seed": seed,
        "checks": assert_contabo_limits_contract(),
    }
