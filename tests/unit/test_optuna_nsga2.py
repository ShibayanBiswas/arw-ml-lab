"""NSGA-II multi-objective Optuna smoke (seed 42)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from labcore.train.tune import run_optuna_tune

ROOT = Path(__file__).resolve().parents[2]


def test_nsga2_quick():
    df = pd.read_csv(ROOT / "data" / "samples" / "titanic.csv")
    df = df.sample(n=min(150, len(df)), random_state=42)
    out = run_optuna_tune(
        df,
        target="Survived",
        algorithm_key="clf.lgbm",
        task="binary",
        preset="quick",
        n_splits=2,
        seed=42,
        n_trials=4,
        sampler="nsga2",
        use_hyperband=True,
    )
    assert out["sampler"] == "nsga2"
    assert out["hyperband"] is True
    assert out["best_params"]
    assert out["n_pareto"] is not None and out["n_pareto"] >= 1
