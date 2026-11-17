"""Offline artefact OPS.OPTUNA.RESUME — resumable Optuna studies (§39.3)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from labcore.train.tune import resolve_optuna_storage, run_optuna_tune

ARTEFACT_ID = "OPS.OPTUNA.RESUME"
STRESS_ID = "ST-OPS-03"


class OptunaResumeContractError(ValueError):
    """Raised when Optuna resume contract fails."""


def assert_resolve_storage_env(monkey_env: dict[str, str] | None = None) -> dict[str, object]:
    import os

    prev = os.environ.get("OPTUNA_STORAGE_URL")
    try:
        if monkey_env:
            os.environ.update(monkey_env)
        if "OPTUNA_STORAGE_URL" in (monkey_env or {}):
            got = resolve_optuna_storage()
            if got != monkey_env["OPTUNA_STORAGE_URL"]:
                raise OptunaResumeContractError("env storage not resolved")
            return {"from_env": True, "url": got}
        explicit = resolve_optuna_storage("sqlite:///tmp/x.db")
        if explicit != "sqlite:///tmp/x.db":
            raise OptunaResumeContractError("explicit storage ignored")
        return {"explicit_ok": True}
    finally:
        if prev is None:
            os.environ.pop("OPTUNA_STORAGE_URL", None)
        else:
            os.environ["OPTUNA_STORAGE_URL"] = prev


def assert_sqlite_resume(*, seed: int = 42, tmp_path: Path | None = None) -> dict[str, object]:
    root = tmp_path or Path(".cache") / "optuna_resume_tests"
    root.mkdir(parents=True, exist_ok=True)
    db = root / f"study_{seed}.db"
    if db.exists():
        db.unlink()
    url = f"sqlite:///{db.resolve().as_posix()}"
    rng = np.random.default_rng(seed)
    n = 60
    df = pd.DataFrame(
        {
            "a": rng.normal(size=n),
            "b": rng.normal(size=n),
            "Survived": (rng.random(size=n) > 0.5).astype(int),
        }
    )
    name = f"resume-test-{seed}"
    first = run_optuna_tune(
        df,
        target="Survived",
        algorithm_key="clf.logistic",
        task="binary",
        preset="quick",
        n_trials=2,
        seed=seed,
        storage=url,
        study_name=name,
    )
    if not first.get("resumable") or first["n_trials_completed"] != 2:
        raise OptunaResumeContractError(f"first run incomplete: {first.get('n_trials_completed')}")
    second = run_optuna_tune(
        df,
        target="Survived",
        algorithm_key="clf.logistic",
        task="binary",
        preset="quick",
        n_trials=4,
        seed=seed,
        storage=url,
        study_name=name,
    )
    if second["n_trials_resumed_from"] != 2:
        raise OptunaResumeContractError(
            f"expected resume from 2, got {second['n_trials_resumed_from']}"
        )
    if second["n_trials_completed"] != 4:
        raise OptunaResumeContractError(
            f"expected 4 completed after resume, got {second['n_trials_completed']}"
        )
    return {
        "first_n": first["n_trials_completed"],
        "second_n": second["n_trials_completed"],
        "resumed_from": second["n_trials_resumed_from"],
        "seed": seed,
    }


def assert_optuna_resume_contract(*, seed: int = 42) -> list[dict[str, object]]:
    return [assert_resolve_storage_env(), assert_sqlite_resume(seed=seed)]


def optuna_resume_manifest(*, seed: int = 42) -> dict[str, object]:
    return {
        "id": ARTEFACT_ID,
        "stress_test": STRESS_ID,
        "seed": seed,
        "checks": assert_optuna_resume_contract(seed=seed),
    }
