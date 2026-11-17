"""Target encoding cross-fitting — MI-02 / ST-ML-02 (ARCHITECTURE §46.1)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import TargetEncoder

from labcore.integrity.target_encoding_policy import (
    MI02_DEFAULT_TARGET_ENCODER_CV,
    MI02_MAX_AUC_DEVIATION,
    MI02_RULE,
    MI02_SYNTHETIC_ROWS,
    auc_deviation_from_chance,
    extract_recipe_target_encoder,
    noise_auc_passes_mi02,
    target_encoder_shuffle,
)
from labcore.preprocess.recipe import RecipeSpec, compile_recipe

ARTEFACT_ID = "MI.TARGET.ENCODING"
STRESS_ID = "ST-ML-02"


class TargetEncodingContractError(ValueError):
    """Raised when MI-02 offline kit contract is violated."""


def assert_mi02_recipe_wires_target_encoder(*, seed: int = 42) -> dict[str, object]:
    """MI-02: ``compile_recipe`` embeds sklearn ``TargetEncoder`` with inner CV."""
    recipe = RecipeSpec(
        categorical_encoder="target",
        target_encoder_cv=MI02_DEFAULT_TARGET_ENCODER_CV,
        scaler="none",
        seed=seed,
    )
    X = pd.DataFrame({"noise_cat": [f"c{i % 40}" for i in range(120)]})
    pre, _cols, meta = compile_recipe(X, recipe)
    if meta["recipe"]["categorical_encoder"] != "target":
        raise TargetEncodingContractError("MI-02: recipe must select target encoder")
    if not hasattr(pre, "named_steps") or "pre" not in pre.named_steps:
        raise TargetEncodingContractError("MI-02: expected sklearn Pipeline with pre step")
    ct = pre.named_steps["pre"]
    enc = extract_recipe_target_encoder(ct)
    if enc is None:
        raise TargetEncodingContractError("MI-02: TargetEncoder missing from recipe pipeline")
    if enc.cv is None:
        raise TargetEncodingContractError("MI-02: TargetEncoder must set cv= for cross-fitting")
    cv_splits = getattr(enc.cv, "n_splits", None)
    if cv_splits != MI02_DEFAULT_TARGET_ENCODER_CV:
        raise TargetEncodingContractError("MI-02: TargetEncoder cv folds must match recipe")
    return {
        "mi_rule": MI02_RULE,
        "categorical_encoder": "target",
        "target_encoder_cv": MI02_DEFAULT_TARGET_ENCODER_CV,
        "encoder_class": type(enc).__name__,
        "seed": seed,
    }


def assert_mi02_noise_column_near_chance(*, seed: int = 42) -> dict[str, object]:
    """MI-02: pure-noise high-cardinality column OOF AUC ≈ chance on synthetic rows."""
    rng = np.random.default_rng(seed)
    n = MI02_SYNTHETIC_ROWS
    x_signal = rng.normal(size=n)
    y = (x_signal + rng.normal(scale=0.3, size=n) > 0).astype(int)
    noise = rng.integers(0, 200, size=n).astype(str)
    X = pd.DataFrame({"noise_cat": noise})
    recipe = RecipeSpec(
        categorical_encoder="target",
        scaler="standard",
        target_encoder_cv=5,
        seed=seed,
    )
    pre, _, _meta = compile_recipe(X, recipe)
    pipe = Pipeline(
        [
            ("pre", pre),
            ("clf", LogisticRegression(max_iter=500, random_state=seed)),
        ]
    )
    proba = cross_val_predict(
        pipe,
        X,
        y,
        cv=StratifiedKFold(5, shuffle=True, random_state=seed),
        method="predict_proba",
    )[:, 1]
    auc = float(roc_auc_score(y, proba))
    if not noise_auc_passes_mi02(auc):
        raise TargetEncodingContractError(
            f"MI-02: noise AUC {auc} deviates from chance by "
            f"{auc_deviation_from_chance(auc):.4f} (max {MI02_MAX_AUC_DEVIATION})"
        )
    return {
        "mi_rule": MI02_RULE,
        "n_rows": n,
        "noise_auc": auc,
        "auc_deviation_from_chance": auc_deviation_from_chance(auc),
        "max_deviation": MI02_MAX_AUC_DEVIATION,
        "seed": seed,
    }


def assert_mi02_full_frame_prefit_leaks(*, seed: int = 42) -> dict[str, object]:
    """MI-02: pre-fitting TargetEncoder on all rows before outer CV fails the guard."""
    rng = np.random.default_rng(seed)
    n = 800
    x_signal = rng.normal(size=n)
    y = (x_signal + rng.normal(scale=0.2, size=n) > 0).astype(int)
    noise = rng.integers(0, 80, size=n).astype(str)
    X = pd.DataFrame({"noise_cat": noise})
    enc = TargetEncoder(smooth="auto", target_type="auto")
    enc.fit(X[["noise_cat"]], y)
    X_leak = enc.transform(X[["noise_cat"]])
    pipe = Pipeline(
        [
            ("clf", LogisticRegression(max_iter=500, random_state=seed)),
        ]
    )
    proba = cross_val_predict(pipe, X_leak, y, cv=5, method="predict_proba")[:, 1]
    auc_leak = float(roc_auc_score(y, proba))
    recipe = RecipeSpec(categorical_encoder="target", scaler="none", seed=seed)
    pre, _, _ = compile_recipe(X, recipe)
    pipe_safe = Pipeline([("pre", pre), ("clf", LogisticRegression(max_iter=500, random_state=seed))])
    proba_safe = cross_val_predict(
        pipe_safe,
        X,
        y,
        cv=StratifiedKFold(5, shuffle=True, random_state=seed),
        method="predict_proba",
    )[:, 1]
    auc_safe = float(roc_auc_score(y, proba_safe))
    if auc_leak <= auc_safe:
        raise TargetEncodingContractError(
            "MI-02: full-frame TargetEncoder prefit should inflate noise AUC vs in-pipeline"
        )
    if not noise_auc_passes_mi02(auc_safe):
        raise TargetEncodingContractError("MI-02: in-pipeline noise AUC must stay near chance")
    return {
        "mi_rule": MI02_RULE,
        "n_rows": n,
        "prefit_auc": auc_leak,
        "pipeline_auc": auc_safe,
        "sequential_shuffle_false": target_encoder_shuffle(sequential=True) is False,
        "seed": seed,
    }


def assert_target_encoding_contract(*, seed: int = 42) -> list[dict[str, object]]:
    return [
        assert_mi02_recipe_wires_target_encoder(seed=seed),
        assert_mi02_noise_column_near_chance(seed=seed),
        assert_mi02_full_frame_prefit_leaks(seed=seed),
    ]


def target_encoding_manifest(*, seed: int = 42) -> dict[str, object]:
    checks = assert_target_encoding_contract(seed=seed)
    return {
        "id": ARTEFACT_ID,
        "stress_test": STRESS_ID,
        "mi_rule": MI02_RULE,
        "seed": seed,
        "checks": checks,
    }