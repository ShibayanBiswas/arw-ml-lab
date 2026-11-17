"""TRAIN.REFIT.FULL wire — TrainConfig + run_supervised_cv (oneshot-c194)."""

from __future__ import annotations

import pandas as pd
from sklearn.datasets import make_classification

from labcore.preprocess.recipe import RecipeSpec
from labcore.train.run import TrainConfig, run_supervised_cv


def _tiny_clf(seed: int = 42) -> pd.DataFrame:
    X, y = make_classification(
        n_samples=80,
        n_features=4,
        n_informative=3,
        n_redundant=0,
        n_classes=2,
        random_state=seed,
    )
    df = pd.DataFrame(X, columns=[f"f{i}" for i in range(X.shape[1])])
    df["target"] = y
    return df


def test_refit_full_default_on_in_result() -> None:
    df = _tiny_clf()
    out = run_supervised_cv(
        df,
        TrainConfig(
            task="binary",
            target="target",
            algorithm_keys=["clf.logistic"],
            n_splits=3,
            seed=42,
            recipe=RecipeSpec(seed=42),
            run_eval=False,
            dataset_id="wire-refit",
        ),
    )
    meta = out.get("refit_full")
    assert meta is not None
    assert meta["artefact"] == "TRAIN.REFIT.FULL"
    assert meta["refit_performed"] is True
    assert meta["policy"]["enabled"] is True
    assert meta["n_excluded_test"] == out["n_test"]
    assert out["champion_pipeline"] is not None


def test_refit_full_toggle_off_skips_fit() -> None:
    df = _tiny_clf()
    out = run_supervised_cv(
        df,
        TrainConfig(
            task="binary",
            target="target",
            algorithm_keys=["clf.logistic"],
            n_splits=3,
            seed=42,
            recipe=RecipeSpec(seed=42),
            run_eval=False,
            dataset_id="wire-refit-off",
            refit_full=False,
        ),
    )
    meta = out["refit_full"]
    assert meta["refit_performed"] is False
    assert meta["policy"]["enabled"] is False
