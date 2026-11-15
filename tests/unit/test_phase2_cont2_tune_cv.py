"""Phase 2-cont-2: Optuna, CV catalogue, MI-02/06, CD, corrected-t, plots, ≥45 algos."""

from __future__ import annotations

import numpy as np
import pandas as pd
from labcore.cv.schemes import CV_SCHEME_IDS, build_splitter, list_cv_schemes, nested_default
from labcore.cv.visualise import iter_splits, plot_cv_folds
from labcore.data.samples import load_sample_frame
from labcore.eval.classification.compare import (
    corrected_resampled_t,
    critical_difference_nemenyi,
)
from labcore.preprocess.recipe import RecipeSpec, compile_recipe
from labcore.registry.algorithms import build_estimator, thin_algorithm_specs
from labcore.registry.catalog import get_catalog
from labcore.train.run import TrainConfig, run_supervised_cv
from labcore.train.tune import run_optuna_tune
from sklearn.datasets import fetch_california_housing, load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline


def test_catalog_at_least_45_and_cv_schemes():
    specs = thin_algorithm_specs()
    assert len(specs) >= 45
    for s in specs:
        est = build_estimator(s)
        assert est is not None
    cat = get_catalog()
    cv_ids = {c["id"] for c in cat.cv}
    assert "stratified_kfold" in cv_ids
    assert "time_series_split" in cv_ids
    assert "nested" in cv_ids
    assert set(CV_SCHEME_IDS) <= cv_ids
    assert any(e["id"] == "target" for e in cat.encoders)
    assert len(list_cv_schemes()) >= 10


def test_nested_default_mi03():
    assert nested_default(1999) is True
    assert nested_default(2000) is False


def test_cv_visualiser_artefact():
    X = np.arange(40).reshape(-1, 1)
    y = np.array([0, 1] * 20)
    splitter = build_splitter("stratified_kfold", n_splits=4, seed=42, task="binary")
    folds = iter_splits(splitter, X, y)
    art = plot_cv_folds(folds, title="test folds")
    assert art["id"] == "CV.P.FOLDS"
    assert "plotly" in art
    assert art["numbers"]["n_folds"] == 4


def test_run_cv_includes_visualiser_and_nested_flag():
    data = load_breast_cancer(as_frame=True)
    df = data.frame.copy()
    df["target"] = data.target
    df = df.sample(n=120, random_state=42)
    out = run_supervised_cv(
        df,
        TrainConfig(
            task="binary",
            target="target",
            algorithm_keys=["clf.logistic"],
            n_splits=3,
            run_eval=False,
        ),
    )
    assert out["n_train"] < 2000
    assert out["nested"] is True
    assert out["cv_visualiser"]["id"] == "CV.P.FOLDS"
    assert "plotly" in out["cv_visualiser"]


def test_optuna_quick_lgbm_fixed_params():
    try:
        df, _, _ = load_sample_frame("DS3")
    except Exception as exc:  # noqa: BLE001
        import pytest

        pytest.skip(f"DS3 unavailable: {exc}")
    # light subsample for speed
    if len(df) > 400:
        df = df.sample(n=400, random_state=42).reset_index(drop=True)
    target = "Survived" if "Survived" in df.columns else df.columns[-1]
    # drop heavy text-like cols already handled in tune; keep numeric-ish
    art = run_optuna_tune(
        df,
        target=target,
        algorithm_key="clf.lgbm",
        task="binary",
        preset="quick",
        n_trials=4,
        n_splits=3,
        fixed_params={"n_estimators": 40, "learning_rate": 0.05},
    )
    assert art["best_params"]["n_estimators"] == 40
    assert art["best_params"]["learning_rate"] == 0.05
    assert art["seed"] == 42
    assert len(art["trials"]) == 4
    assert art["mlflow"]["logged"] is False


def test_mi02_target_encoder_noise_near_chance():
    """Noise categorical TargetEncoded inside CV stays ~chance (MI-02)."""
    rng = np.random.default_rng(42)
    n = 400
    x_signal = rng.normal(size=n)
    y = (x_signal + rng.normal(scale=0.3, size=n) > 0).astype(int)
    noise = rng.integers(0, 50, size=n).astype(str)
    X = pd.DataFrame({"signal": x_signal, "noise_cat": noise})
    recipe = RecipeSpec(categorical_encoder="target", scaler="standard", seed=42)
    pre, _, meta = compile_recipe(X[["noise_cat"]], recipe)
    assert meta["recipe"]["categorical_encoder"] == "target"
    # Only noise column — OOF predictions via TargetEncoder + logistic
    pipe = Pipeline(
        [
            ("pre", pre),
            ("clf", LogisticRegression(max_iter=500, random_state=42)),
        ]
    )
    proba = cross_val_predict(
        pipe,
        X[["noise_cat"]],
        y,
        cv=StratifiedKFold(5, shuffle=True, random_state=42),
        method="predict_proba",
    )[:, 1]
    auc = float(roc_auc_score(y, proba))
    assert 0.40 <= auc <= 0.60, f"noise AUC leaked: {auc}"


def test_mi06_quick_reproducible():
    data = load_breast_cancer(as_frame=True)
    df = data.frame.copy()
    df["target"] = data.target
    df = df.sample(n=150, random_state=42)
    cfg = TrainConfig(
        task="binary",
        target="target",
        algorithm_keys=["clf.logistic"],
        n_splits=3,
        seed=42,
        run_eval=False,
    )
    a = run_supervised_cv(df, cfg)
    b = run_supervised_cv(df, cfg)
    assert a["leaderboard"][0]["cv_mean"] == b["leaderboard"][0]["cv_mean"]
    assert a["leaderboard"][0]["test"] == b["leaderboard"][0]["test"]


def test_cd_nemenyi_synthetic():
    # 5 folds × 4 models — clear ranking
    fold_scores = {
        "A": [0.9, 0.88, 0.91, 0.89, 0.90],
        "B": [0.7, 0.72, 0.71, 0.69, 0.70],
        "C": [0.5, 0.52, 0.51, 0.49, 0.50],
        "D": [0.6, 0.61, 0.59, 0.62, 0.60],
    }
    out = critical_difference_nemenyi(fold_scores)
    assert out["id"] == "CLE.P.CD"
    assert out["friedman_p"] is not None
    assert out["friedman_p"] < 0.05
    assert out["avg_rank"]["A"] < out["avg_rank"]["C"]


def test_corrected_t_golden():
    # Fixed synthetic — hand-checked Nadeau-Bengio formula
    scores_a = np.array([0.80, 0.82, 0.79, 0.81, 0.805])
    scores_b = np.array([0.75, 0.76, 0.74, 0.755, 0.748])
    n_train, n_test = 80, 20
    d = scores_a - scores_b
    mean_d = float(d.mean())
    var_d = float(d.var(ddof=1))
    n = len(d)
    corr = (1.0 / n) + (n_test / n_train)
    expected_t = mean_d / np.sqrt(corr * var_d)
    out = corrected_resampled_t(scores_a, scores_b, n_train=n_train, n_test=n_test)
    assert abs(out["t_statistic"] - expected_t) < 1e-12
    assert out["pvalue"] is not None
    assert out["pvalue"] < 0.05


def test_expanded_cle_plots_ds4():
    data = load_breast_cancer(as_frame=True)
    df = data.frame.copy()
    df["target"] = data.target
    df = df.sample(n=200, random_state=42)
    out = run_supervised_cv(
        df,
        TrainConfig(
            task="binary",
            target="target",
            algorithm_keys=["clf.logistic"],
            n_splits=3,
            run_eval=True,
        ),
    )
    plots = out["eval"]["classification"]["plots"]
    ids = {p["id"] for p in plots}
    for need in (
        "CLE.P.GAINS",
        "CLE.P.LIFT",
        "CLE.P.KS",
        "CLE.P.THRESHOLD",
        "CLE.P.DET",
        "CLE.P.PROB_DENS",
        "CLE.P.PER_CLASS_PRF",
    ):
        assert need in ids


def test_expanded_ree_plots_ds12_fixture():
    try:
        data = fetch_california_housing(as_frame=True)
    except Exception as exc:  # noqa: BLE001
        import pytest

        pytest.skip(f"california housing unavailable: {exc}")
    df = data.frame.copy()
    df["target"] = data.target
    df = df.sample(n=250, random_state=42)
    out = run_supervised_cv(
        df,
        TrainConfig(
            task="regression",
            target="target",
            algorithm_keys=["reg.ridge"],
            n_splits=3,
            run_eval=True,
        ),
    )
    plots = out["eval"]["regression"]["plots"]
    ids = {p["id"] for p in plots}
    for need in (
        "REE.P.COOKS",
        "REE.P.STUD_RESID",
        "REE.P.BLAND_ALTMAN",
        "REE.P.RESID_ACF",
    ):
        assert need in ids
