"""Contabo single-heavy-job alias — DEPLOY_CONTABO §12 (oneshot-c205/c206).

Delegates to ``OPS.CONTABO.LIMITS`` so concurrency=1 stays a single source of truth.
"""

from __future__ import annotations

from typing import Any

from labcore.ops.contabo_limits_contract import (
    ARTEFACT_ID as LIMITS_ID,
    assert_worker_train_one_heavy,
    contabo_limits_manifest,
)

ARTEFACT_ID = "OPS.CONTABO.CONCURRENCY"


def assert_train_concurrency_one() -> dict[str, object]:
    check = assert_worker_train_one_heavy()
    return {
        "service": "worker-train",
        "concurrency": str(check.get("concurrency", "1")),
        "gpu": "false",
        "source": LIMITS_ID,
    }


def contabo_concurrency_manifest(*, seed: int = 42) -> dict[str, Any]:
    limits = contabo_limits_manifest(seed=seed)
    return {
        "id": ARTEFACT_ID,
        "seed": seed,
        "policy": "one_heavy_job",
        "check": assert_train_concurrency_one(),
        "limits_artefact": limits["id"],
    }


def assert_contabo_concurrency_contract() -> dict[str, object]:
    return contabo_concurrency_manifest(seed=42)
