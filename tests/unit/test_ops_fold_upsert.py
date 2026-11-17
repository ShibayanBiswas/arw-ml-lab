"""OPS.FOLD.UPSERT — idempotent fold writes (oneshot-c188)."""

from __future__ import annotations

from labcore.ops.fold_upsert_contract import ARTEFACT_ID, STRESS_ID, fold_upsert_manifest


def test_fold_upsert_manifest_seed_42() -> None:
    m = fold_upsert_manifest(seed=42)
    assert m["id"] == ARTEFACT_ID
    assert m["stress_test"] == STRESS_ID
    assert m["seed"] == 42
    assert len(m["checks"]) == 3
