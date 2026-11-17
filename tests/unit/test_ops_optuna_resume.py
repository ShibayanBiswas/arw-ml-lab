"""OPS.OPTUNA.RESUME — resumable Optuna studies (oneshot-c189)."""

from __future__ import annotations

from labcore.ops.optuna_resume_contract import ARTEFACT_ID, STRESS_ID, optuna_resume_manifest


def test_optuna_resume_manifest_seed_42() -> None:
    m = optuna_resume_manifest(seed=42)
    assert m["id"] == ARTEFACT_ID
    assert m["stress_test"] == STRESS_ID
    assert m["seed"] == 42
    assert m["checks"][1]["second_n"] == 4
    assert m["checks"][1]["resumed_from"] == 2
