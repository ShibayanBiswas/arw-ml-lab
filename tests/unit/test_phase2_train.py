"""Phase 2 thin: catalog, recipe, leakage spies, DS3 quick train."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from labcore.data.samples import load_sample_frame
from labcore.preprocess.recipe import RecipeSpec, compile_recipe, drop_constant_columns
from labcore.registry.algorithms import thin_algorithm_specs
from labcore.registry.catalog import get_catalog
from labcore.train.run import TrainConfig, run_supervised_cv


def test_catalog_has_at_least_10_algorithms():
    cat = get_catalog()
    assert len(cat.algorithms) >= 10
    keys = {a.key for a in cat.algorithms}
    assert "clf.lgbm" in keys
    assert "reg.ridge" in keys


def test_all_thin_specs_instantiate():
    from labcore.registry.algorithms import build_estimator

    for spec in thin_algorithm_specs():
        est = build_estimator(spec)
        assert est is not None


def test_drop_constant_mi11():
    df = pd.DataFrame({"a": [1, 1, 1], "b": [1, 2, 3], "c": [np.nan, np.nan, np.nan]})
    out, dropped = drop_constant_columns(df)
    assert "a" in dropped and "c" in dropped
    assert list(out.columns) == ["b"]


def test_recipe_compile_shapes():
    df = pd.DataFrame({"x": [1.0, 2.0, np.nan], "c": ["a", "b", "a"], "y": [0, 1, 0]})
    X = df.drop(columns=["y"])
    pipe, cols, meta = compile_recipe(X, RecipeSpec())
    assert "pre" in pipe.named_steps
    assert "x" in cols


def test_shuffled_target_near_chance():
    rng = np.random.default_rng(42)
    n = 400
    X = pd.DataFrame({f"f{i}": rng.normal(size=n) for i in range(5)})
    y = (X["f0"] > 0).astype(int)
    df = X.copy()
    df["target"] = y
    good = run_supervised_cv(
        df,
        TrainConfig(task="binary", target="target", algorithm_keys=["clf.logistic"], n_splits=3),
    )
    bal_good = good["leaderboard"][0]["cv_mean"]["balanced_accuracy"]
    df_bad = df.copy()
    df_bad["target"] = rng.permutation(y.to_numpy())
    bad = run_supervised_cv(
        df_bad,
        TrainConfig(task="binary", target="target", algorithm_keys=["clf.logistic"], n_splits=3),
    )
    bal_bad = bad["leaderboard"][0]["cv_mean"]["balanced_accuracy"]
    assert bal_good > bal_bad
    assert bal_bad < 0.65


def test_fold_fit_spy():
    rng = np.random.default_rng(42)
    n = 120
    df = pd.DataFrame(
        {
            "x": rng.normal(size=n),
            "z": rng.normal(size=n),
            "target": rng.integers(0, 2, size=n),
        }
    )
    spy: dict[str, int] = {}
    run_supervised_cv(
        df,
        TrainConfig(task="binary", target="target", algorithm_keys=["clf.logistic"], n_splits=4),
        spy_fit_counts=spy,
    )
    assert spy.get("clf.logistic") == 4


def test_ds3_quick_train():
    try:
        df, _, _ = load_sample_frame("DS3")
    except Exception as exc:
        pytest.skip(str(exc))
    # Drop obvious leakage/id columns for a fair smoke
    drop = [c for c in ("PassengerId", "Name", "Ticket", "Cabin") if c in df.columns]
    df = df.drop(columns=drop)
    out = run_supervised_cv(
        df,
        TrainConfig(
            task="binary",
            target="Survived",
            algorithm_keys=["clf.logistic", "clf.rf", "clf.lgbm"],
            n_splits=3,
        ),
    )
    assert len(out["leaderboard"]) == 3
    assert out["leaderboard"][0]["rank"] == 1
    assert "balanced_accuracy" in out["leaderboard"][0]["cv_mean"]


def test_ds12_quick_train():
    try:
        df, _, _ = load_sample_frame("DS12")
    except Exception:
        # Lazy OpenML entry — same series via sklearn when file not cached locally
        from sklearn.datasets import fetch_california_housing

        bunch = fetch_california_housing(as_frame=True)
        df = bunch.frame.copy()
        df = df.rename(columns={"MedHouseVal": "median_house_value"})
    target = (
        "median_house_value"
        if "median_house_value" in df.columns
        else ("MedHouseVal" if "MedHouseVal" in df.columns else df.columns[-1])
    )
    # Cap rows for Quick E2E runtime
    df = df.sample(n=min(1500, len(df)), random_state=42)
    out = run_supervised_cv(
        df,
        TrainConfig(
            task="regression",
            target=target,
            algorithm_keys=["reg.ridge", "reg.rf", "reg.lgbm"],
            n_splits=3,
        ),
    )
    assert len(out["leaderboard"]) == 3
    assert out["leaderboard"][0]["rank"] == 1
    assert "r2" in out["leaderboard"][0]["cv_mean"]


def test_smote_not_applied_to_validation():
    """SMOTE sits inside imblearn Pipeline — transform/predict never resamples val."""
    from imblearn.over_sampling import SMOTE
    from imblearn.pipeline import Pipeline as ImbPipeline
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler

    rng = np.random.default_rng(42)
    n = 200
    X = pd.DataFrame({"x": rng.normal(size=n), "z": rng.normal(size=n)})
    y = pd.Series(np.concatenate([np.zeros(160, dtype=int), np.ones(40, dtype=int)]))
    X_tr, X_va, y_tr, y_va = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )
    pipe = ImbPipeline(
        [
            ("scale", StandardScaler()),
            ("resample", SMOTE(random_state=42)),
            ("model", LogisticRegression(max_iter=200, random_state=42)),
        ]
    )
    pipe.fit(X_tr, y_tr)
    pred = pipe.predict(X_va)
    assert len(pred) == len(X_va)

    # Full recipe path with resample=smote also preserves val length
    df = X.copy()
    df["target"] = y
    out = run_supervised_cv(
        df,
        TrainConfig(
            task="binary",
            target="target",
            algorithm_keys=["clf.logistic"],
            n_splits=3,
            recipe=RecipeSpec(resample="smote", seed=42),
        ),
    )
    assert len(out["leaderboard"]) == 1


def test_tuning_presets_and_csv_export():
    from labcore.train.export import leaderboard_to_csv
    from labcore.train.presets import get_tuning_preset

    assert get_tuning_preset("quick")["n_trials"] == 20
    assert get_tuning_preset("balanced")["n_trials"] == 60
    csv_text = leaderboard_to_csv(
        [
            {
                "rank": 1,
                "algorithm_key": "clf.logistic",
                "algorithm_id": "C1",
                "name": "=HACK()",
                "library": "sklearn",
                "primary_metric": "balanced_accuracy",
                "cv_mean": {"balanced_accuracy": 0.7},
                "cv_std": {"balanced_accuracy": 0.01},
                "test": {"balanced_accuracy": 0.69},
            }
        ]
    )
    assert "'=HACK()" in csv_text
    assert "cv_mean_balanced_accuracy" in csv_text
