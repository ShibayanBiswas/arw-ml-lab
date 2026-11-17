"""OPS.SOFT.TIME_LIMIT — best-so-far on soft limit (oneshot-c186)."""

from __future__ import annotations

from labcore.ops.soft_time_limit_contract import (
    ARTEFACT_ID,
    STRESS_ID,
    soft_time_limit_manifest,
)


def test_soft_time_limit_manifest_seed_42() -> None:
    m = soft_time_limit_manifest(seed=42)
    assert m["id"] == ARTEFACT_ID
    assert m["stress_test"] == STRESS_ID
    assert m["seed"] == 42
    assert len(m["checks"]) == 4
