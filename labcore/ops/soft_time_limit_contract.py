"""Offline artefact OPS.SOFT.TIME_LIMIT — best-so-far on soft limit."""

from __future__ import annotations

from pathlib import Path

from labcore.ops.soft_time_limit import (
    ARTEFACT_ID,
    STRESS_ID,
    PartialHolder,
    is_soft_time_limit_exc,
    sanitize_leaderboard_rows,
    save_best_so_far,
    truncated_result,
)

ROOT = Path(__file__).resolve().parents[2]
TRAIN_TASK = ROOT / "backend" / "worker" / "tasks" / "train.py"
TUNE_TASK = ROOT / "backend" / "worker" / "tasks" / "tune.py"
TRAIN_RUN = ROOT / "labcore" / "train" / "run.py"
TUNE_RUN = ROOT / "labcore" / "train" / "tune.py"


class SoftTimeLimitContractError(ValueError):
    """Raised when soft-limit contract fails."""


class SoftTimeLimitExceeded(Exception):
    """Stand-in for Celery/billiard SoftTimeLimitExceeded (name must match)."""


def assert_truncated_payload(*, seed: int = 42) -> dict[str, object]:
    out = truncated_result({"leaderboard": [{"rank": 1}]}, seed=seed)
    if not out["truncated"] or out["truncation_reason"] != "soft_time_limit":
        raise SoftTimeLimitContractError("truncated flags missing")
    if out["artefact"] != ARTEFACT_ID:
        raise SoftTimeLimitContractError("artefact id")
    return {"truncated": True, "seed": seed}


def assert_detect_soft_exc() -> dict[str, object]:
    if not is_soft_time_limit_exc(SoftTimeLimitExceeded()):
        raise SoftTimeLimitContractError("must detect SoftTimeLimitExceeded by name")
    if is_soft_time_limit_exc(ValueError("x")):
        raise SoftTimeLimitContractError("must not treat ValueError as soft limit")
    return {"detect_ok": True}


def assert_save_best_so_far(*, seed: int = 42) -> dict[str, object]:
    jobs: list[dict[str, object]] = []
    exps: list[dict[str, object]] = []

    def job_update(job_id: str, **kwargs: object) -> None:
        jobs.append({"job_id": job_id, **kwargs})

    def exp_update(experiment_id: str, **kwargs: object) -> None:
        exps.append({"experiment_id": experiment_id, **kwargs})

    result = save_best_so_far(
        job_update=job_update,
        experiment_update=exp_update,
        job_id="j1",
        experiment_id="e1",
        partial={"leaderboard": [{"algorithm_key": "clf.lgbm"}]},
        seed=seed,
    )
    if not result["truncated"] or jobs[0]["status"] != "done":
        raise SoftTimeLimitContractError("save_best_so_far job status")
    if exps[0]["status"] != "done":
        raise SoftTimeLimitContractError("experiment not marked done")
    return {"job_updates": len(jobs), "exp_updates": len(exps), "seed": seed}


def assert_train_task_handles_soft() -> dict[str, object]:
    src = TRAIN_TASK.read_text(encoding="utf-8")
    for needle in (
        "is_soft_time_limit_exc",
        "save_best_so_far",
        "soft_time_limit",
        "PartialHolder",
        "on_partial",
    ):
        if needle not in src:
            raise SoftTimeLimitContractError(f"train task missing {needle}")
    return {"train_wired": True}


def assert_tune_task_handles_soft() -> dict[str, object]:
    src = TUNE_TASK.read_text(encoding="utf-8")
    for needle in ("is_soft_time_limit_exc", "save_best_so_far", "PartialHolder", "on_partial"):
        if needle not in src:
            raise SoftTimeLimitContractError(f"tune task missing {needle}")
    return {"tune_wired": True}


def assert_mid_run_partial_hooks() -> dict[str, object]:
    """Train/tune library loops must accept on_partial for mid-run checkpoints."""
    run_src = TRAIN_RUN.read_text(encoding="utf-8")
    tune_src = TUNE_RUN.read_text(encoding="utf-8")
    if "on_partial" not in run_src:
        raise SoftTimeLimitContractError("run_supervised_cv missing on_partial")
    if "on_partial" not in tune_src:
        raise SoftTimeLimitContractError("run_optuna_tune missing on_partial")
    holder = PartialHolder()
    holder.update({"leaderboard": [{"algorithm_key": "clf.lgbm"}], "n_models_done": 1})
    if not holder.value or "leaderboard" not in holder.value:
        raise SoftTimeLimitContractError("PartialHolder.update failed")
    clean = sanitize_leaderboard_rows(
        [{"algorithm_key": "a", "_pipeline": object(), "_oof": {}}]
    )
    if "_pipeline" in clean[0] or "_oof" in clean[0]:
        raise SoftTimeLimitContractError("sanitize must drop private keys")
    return {"mid_run_hooks": True, "holder_ok": True}


def assert_soft_time_limit_contract(*, seed: int = 42) -> list[dict[str, object]]:
    return [
        assert_truncated_payload(seed=seed),
        assert_detect_soft_exc(),
        assert_save_best_so_far(seed=seed),
        assert_train_task_handles_soft(),
        assert_tune_task_handles_soft(),
        assert_mid_run_partial_hooks(),
    ]


def soft_time_limit_manifest(*, seed: int = 42) -> dict[str, object]:
    return {
        "id": ARTEFACT_ID,
        "stress_test": STRESS_ID,
        "seed": seed,
        "checks": assert_soft_time_limit_contract(seed=seed),
    }
