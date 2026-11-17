"""Seed drift / reproducibility — MI-06 / ST-ML-02 (ARCHITECTURE §46.1)."""

from __future__ import annotations

from sklearn.datasets import load_breast_cancer

from labcore.integrity.seed_drift_policy import (
    LAB_DEFAULT_SEED,
    METRIC_REPRODUCE_ATOL,
    MI06_RULE,
    apply_lab_seed,
    metrics_close,
    metrics_differ,
)
from labcore.train.run import TrainConfig, run_supervised_cv

ARTEFACT_ID = "MI.SEED.DRIFT"
STRESS_ID = "ST-ML-02"
DRIFT_SEED = 43


class SeedDriftContractError(ValueError):
    """Raised when MI-06 offline kit contract is violated."""


def _quick_breast_cancer_frame(*, seed: int = LAB_DEFAULT_SEED):
    data = load_breast_cancer(as_frame=True)
    df = data.frame.copy()
    df["target"] = data.target
    return df.sample(n=150, random_state=seed)


def _cv_leaderboard_mean(*, seed: int) -> float:
    apply_lab_seed(seed)
    df = _quick_breast_cancer_frame(seed=seed)
    cfg = TrainConfig(
        task="binary",
        target="target",
        algorithm_keys=["clf.logistic"],
        n_splits=3,
        seed=seed,
        run_eval=False,
    )
    out = run_supervised_cv(df, cfg)
    row = out["leaderboard"][0]
    primary = str(row["primary_metric"])
    return float(row["cv_mean"][primary])


def assert_mi06_quick_run_reproduces(*, seed: int = LAB_DEFAULT_SEED) -> dict[str, object]:
    """MI-06: two Quick runs with the same seed match to 1e-12 (CPU)."""
    apply_lab_seed(seed)
    a = _cv_leaderboard_mean(seed=seed)
    apply_lab_seed(seed)
    b = _cv_leaderboard_mean(seed=seed)
    if not metrics_close(a, b, atol=METRIC_REPRODUCE_ATOL):
        raise SeedDriftContractError(
            f"MI-06: duplicate runs must match within {METRIC_REPRODUCE_ATOL}: {a} vs {b}"
        )
    return {
        "mi_rule": MI06_RULE,
        "lab_default_seed": LAB_DEFAULT_SEED,
        "cv_mean": a,
        "reproduced": True,
        "atol": METRIC_REPRODUCE_ATOL,
        "seed": seed,
    }


def assert_mi06_seed_change_drifts(*, seed: int = LAB_DEFAULT_SEED) -> dict[str, object]:
    """MI-06 negative: shuffled subsample with a different seed changes the CV mean."""
    a = _cv_leaderboard_mean(seed=seed)
    b = _cv_leaderboard_mean(seed=DRIFT_SEED)
    if not metrics_differ(a, b, atol=METRIC_REPRODUCE_ATOL):
        raise SeedDriftContractError("MI-06: seed change must drift metrics on subsample fixture")
    return {
        "mi_rule": MI06_RULE,
        "cv_mean_seed_42": a,
        "cv_mean_seed_43": b,
        "drift_detected": True,
        "seed": seed,
    }


def assert_seed_drift_contract(*, seed: int = LAB_DEFAULT_SEED) -> list[dict[str, object]]:
    return [
        assert_mi06_quick_run_reproduces(seed=seed),
        assert_mi06_seed_change_drifts(seed=seed),
    ]


def seed_drift_manifest(*, seed: int = LAB_DEFAULT_SEED) -> dict[str, object]:
    checks = assert_seed_drift_contract(seed=seed)
    return {
        "id": ARTEFACT_ID,
        "stress_test": STRESS_ID,
        "mi_rule": MI06_RULE,
        "seed": seed,
        "checks": checks,
    }