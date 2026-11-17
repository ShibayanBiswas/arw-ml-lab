"""Contabo single-heavy-job policy — DEPLOY_CONTABO §12 (oneshot-c205).

``worker-train`` runs with Celery concurrency 1 so only one train/tune/forecast
job occupies the 3.5 GB budget at a time. GPU models stay refused (422).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

ARTEFACT_ID = "OPS.CONTABO.CONCURRENCY"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def assert_train_concurrency_one(compose_text: str | None = None) -> dict[str, str]:
    text = compose_text or (_repo_root() / "docker-compose.prod.yml").read_text(encoding="utf-8")
    # Locate worker-train command block
    if "worker-train:" not in text:
        raise AssertionError("worker-train service missing")
    block = text.split("worker-train:", 1)[1].split("\n  ", 1)[0]
    # Prefer reading until next top-level service — simpler: search nearby concurrency
    section = text.split("worker-train:", 1)[1]
    # Until lab-beat or next service at 2-space indent after blank
    end = section.find("\n  lab-beat:")
    if end == -1:
        end = section.find("\n  mlflow:")
    chunk = section[: end if end != -1 else 800]
    if "--concurrency" not in chunk:
        raise AssertionError("worker-train must set --concurrency")
    # Expect "- \"1\"" after --concurrency
    if '- "1"' not in chunk and "- '1'" not in chunk and "\n      - \"1\"" not in chunk:
        raise AssertionError("worker-train concurrency must be 1 on Contabo")
    if "LAB_GPU_WORKER" in chunk and '"false"' not in chunk and "'false'" not in chunk:
        # env may use false without quotes
        if "false" not in chunk.lower():
            raise AssertionError("LAB_GPU_WORKER must be false on Contabo train")
    return {"service": "worker-train", "concurrency": "1", "gpu": "false"}


def contabo_concurrency_manifest(*, seed: int = 42) -> dict[str, Any]:
    check = assert_train_concurrency_one()
    return {"id": ARTEFACT_ID, "seed": seed, "policy": "one_heavy_job", "check": check}


def assert_contabo_concurrency_contract() -> dict[str, object]:
    return contabo_concurrency_manifest(seed=42)
