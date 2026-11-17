"""OPS.CONTABO.LIMITS — DEPLOY_CONTABO §5/§12 (oneshot-c185)."""

from __future__ import annotations

from labcore.ops.contabo_limits_contract import (
    ARTEFACT_ID,
    STRESS_ID,
    contabo_limits_manifest,
)


def test_contabo_limits_manifest_seed_42() -> None:
    m = contabo_limits_manifest(seed=42)
    assert m["id"] == ARTEFACT_ID
    assert m["stress_test"] == STRESS_ID
    assert m["seed"] == 42
    assert len(m["checks"]) == 4
    assert m["checks"][0]["concurrency"] == 1
