"""OPS.SOFT.TIME_LIMIT — best-so-far on soft limit (oneshot-c186 / c272 mid-run)."""

from __future__ import annotations

import pandas as pd
from labcore.ops.soft_time_limit import PartialHolder, sanitize_leaderboard_rows
from labcore.ops.soft_time_limit_contract import (
    ARTEFACT_ID,
    SoftTimeLimitExceeded,
    STRESS_ID,
    soft_time_limit_manifest,
)
from labcore.ops.soft_time_limit import is_soft_time_limit_exc, save_best_so_far
from labcore.preprocess.recipe import RecipeSpec
from labcore.train.run import TrainConfig, run_supervised_cv
from labcore.train.tune import run_optuna_tune


def test_soft_time_limit_manifest_seed_42() -> None:
    m = soft_time_limit_manifest(seed=42)
    assert m["id"] == ARTEFACT_ID
    assert m["stress_test"] == STRESS_ID
    assert m["seed"] == 42
    assert len(m["checks"]) == 7


def test_sanitize_drops_private_keys() -> None:
    rows = sanitize_leaderboard_rows(
        [{"algorithm_key": "clf.lgbm", "_pipeline": object(), "_oof": {"x": 1}}]
    )
    assert rows == [{"algorithm_key": "clf.lgbm"}]


def test_train_on_partial_fills_holder_before_soft_kill() -> None:
    """Mid-CV soft kill must see completed algorithms in PartialHolder."""
    df = pd.DataFrame(
        {
            "a": list(range(24)),
            "b": [i % 3 for i in range(24)],
            "y": [i % 2 for i in range(24)],
        }
    )
    holder = PartialHolder()
    n_calls = {"n": 0}

    def on_partial(snap: dict) -> None:
        n_calls["n"] += 1
        holder.update(snap)
        if n_calls["n"] >= 1:
            raise SoftTimeLimitExceeded()

    cfg = TrainConfig(
        task="binary",
        target="y",
        algorithm_keys=["clf.logistic", "clf.ridge"],
        n_splits=2,
        seed=42,
        recipe=RecipeSpec(seed=42),
        run_eval=False,
        refit_full=False,
        cv_scheme="kfold",
        nested=False,
    )
    raised = False
    try:
        run_supervised_cv(df, cfg, on_partial=on_partial)
    except SoftTimeLimitExceeded:
        raised = True
    assert raised
    assert is_soft_time_limit_exc(SoftTimeLimitExceeded())
    assert holder.value is not None
    assert holder.value.get("n_models_done", 0) >= 1
    assert holder.value["leaderboard"]
    assert all(not k.startswith("_") for row in holder.value["leaderboard"] for k in row)

    jobs: list[dict] = []

    def job_update(job_id: str, **kwargs: object) -> None:
        jobs.append({"job_id": job_id, **kwargs})

    out = save_best_so_far(
        job_update=job_update,
        experiment_update=None,
        job_id="j-soft",
        experiment_id=None,
        partial=holder.value,
        seed=42,
    )
    assert out["truncated"] is True
    assert out["n_models_done"] >= 1
    assert jobs[0]["status"] == "done"


def test_tune_on_partial_emits_best_so_far() -> None:
    df = pd.DataFrame(
        {
            "a": [float(i) for i in range(40)],
            "b": [float(i % 3) for i in range(40)],
            "y": [i % 2 for i in range(40)],
        }
    )
    holder = PartialHolder()

    def on_partial(snap: dict) -> None:
        holder.update(snap)

    result = run_optuna_tune(
        df,
        target="y",
        algorithm_key="clf.logistic",
        task="binary",
        preset="quick",
        n_splits=2,
        seed=42,
        recipe=RecipeSpec(seed=42),
        n_trials=2,
        on_partial=on_partial,
    )
    assert holder.value is not None
    assert holder.value.get("partial_checkpoint") is True
    assert holder.value.get("n_trials_completed", 0) >= 1
    assert result["n_trials_completed"] == 2
