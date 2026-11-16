"""HalvingRandomSearchCV tune smoke (seed 42)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from labcore.train.tune import run_halving_tune

ROOT = Path(__file__).resolve().parents[2]


def test_halving_lgbm_titanic():
    df = pd.read_csv(ROOT / "data" / "samples" / "titanic.csv")
    # small subsample for speed
    df = df.sample(n=min(200, len(df)), random_state=42)
    out = run_halving_tune(
        df,
        target="Survived",
        algorithm_key="clf.lgbm",
        task="binary",
        n_splits=2,
        seed=42,
        n_candidates=6,
    )
    assert out["method"] == "halving_random"
    assert out["best_params"]
    assert out["best_value"] == out["best_value"]  # not nan
