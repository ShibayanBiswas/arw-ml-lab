"""Class imbalance / fold-internal resampling — MI-07 / ST-ML-02 (ARCHITECTURE §46.1)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.preprocessing import StandardScaler

from labcore.integrity.class_imbalance_policy import (
    EXTREME_RARITY_MINORITY_ROWS,
    IMBALANCE_MINORITY_SHARE,
    IMBALANCE_RATIO_MAX,
    MI07_RULE,
    smote_inflates_train_only,
    validation_prediction_length_unchanged,
)
from labcore.integrity.preprocess_fit_policy import FitIndexSpy, fit_indices_match_train
from labcore.integrity.sample_size_policy import classify_class_imbalance
from labcore.preprocess.recipe import RecipeSpec, compile_recipe

ARTEFACT_ID = "MI.CLASS.RESAMPLE"
STRESS_ID = "ST-ML-02"


class ClassImbalanceContractError(ValueError):
    """Raised when MI-07 offline kit contract is violated."""


def assert_mi07_imbalance_detection(*, seed: int = 42) -> dict[str, object]:
    """MI-07: minority share and ratio gates match ARCHITECTURE §46.1."""
    _ = seed
    skew = classify_class_imbalance([0] * 85 + [1] * 15)
    if not skew["imbalanced"]:
        raise ClassImbalanceContractError("MI-07: 15 % minority must flag imbalanced")
    if skew["minority_share"] >= IMBALANCE_MINORITY_SHARE:
        raise ClassImbalanceContractError("MI-07: skew fixture below minority share gate")
    ratio_only = classify_class_imbalance([0] * 85 + [1] * 15)
    if not ratio_only["imbalanced"]:
        raise ClassImbalanceContractError("MI-07: 85/15 split must flag imbalanced")
    if ratio_only["imbalance_ratio"] <= IMBALANCE_RATIO_MAX:
        raise ClassImbalanceContractError("MI-07: ratio gate fixture must exceed 4")
    rare = classify_class_imbalance([0] * 28 + [1] * 2)
    if not rare["extreme_rarity"]:
        raise ClassImbalanceContractError(
            f"MI-07: minority < {EXTREME_RARITY_MINORITY_ROWS} rows must set extreme_rarity"
        )
    if not rare["recommend_repeated_stratified_cv"]:
        raise ClassImbalanceContractError("MI-07: extreme rarity must propose repeated stratified CV")
    balanced = classify_class_imbalance([0] * 50 + [1] * 50)
    if balanced["imbalanced"]:
        raise ClassImbalanceContractError("MI-07: 50/50 must not be imbalanced")
    return {
        "mi_rule": MI07_RULE,
        "skew_minority_share": skew["minority_share"],
        "extreme_rarity": rare["extreme_rarity"],
        "balanced_ok": not balanced["imbalanced"],
        "seed": seed,
    }


def assert_mi07_smote_resampler_fold_train_only(*, seed: int = 42) -> dict[str, object]:
    """MI-07: SMOTE inside imblearn Pipeline fits only on fold train rows; val len unchanged."""
    from imblearn.over_sampling import SMOTE  # type: ignore[import-untyped]
    from imblearn.pipeline import Pipeline as ImbPipeline  # type: ignore[import-untyped]

    rng = np.random.default_rng(seed)
    n = 200
    X = pd.DataFrame(
        {"x1": rng.normal(size=n), "x2": rng.normal(size=n)},
        index=pd.RangeIndex(0, n),
    )
    y = np.concatenate([np.zeros(160, dtype=int), np.ones(40, dtype=int)])
    pipe = ImbPipeline(
        [
            ("spy", FitIndexSpy()),
            ("scale", StandardScaler()),
            ("resample", SMOTE(random_state=seed)),
            ("model", LogisticRegression(max_iter=300, random_state=seed)),
        ],
    )
    cv = StratifiedKFold(n_splits=4, shuffle=True, random_state=seed)
    out = cross_validate(
        pipe,
        X,
        y,
        cv=cv,
        return_estimator=True,
        scoring="accuracy",
    )
    folds_ok = 0
    for est, (tr_idx, va_idx) in zip(out["estimator"], cv.split(X, y)):
        spy = est.named_steps["spy"]
        if spy.fit_indices_ is None:
            raise ClassImbalanceContractError("MI-07: spy missing fit_indices_ before resample")
        if not fit_indices_match_train(spy.fit_indices_, tr_idx, index=X.index):
            raise ClassImbalanceContractError("MI-07: resampler pipeline fit must see train rows only")
        X_va = X.iloc[va_idx]
        if not validation_prediction_length_unchanged(est, X_va.to_numpy()):
            raise ClassImbalanceContractError("MI-07: validation predictions must match val row count")
        n_tr = len(tr_idx)
        resampled = est.named_steps["resample"]
        n_after = int(getattr(resampled, "sample_indices_", np.arange(n_tr)).shape[0])
        if not smote_inflates_train_only(n_tr, n_after, n_val=len(va_idx)):
            raise ClassImbalanceContractError("MI-07: SMOTE must upsample train without touching val")
        folds_ok += 1
    return {
        "mi_rule": MI07_RULE,
        "n_rows": n,
        "n_splits": 4,
        "folds_verified": folds_ok,
        "resample": "smote",
        "seed": seed,
    }


def assert_mi07_recipe_wires_smote(*, seed: int = 42) -> dict[str, object]:
    """MI-07: ``compile_recipe`` embeds SMOTE in ``imblearn.pipeline.Pipeline``."""
    from imblearn.pipeline import Pipeline as ImbPipeline  # type: ignore[import-untyped]

    recipe = RecipeSpec(resample="smote", scaler="standard", seed=seed)
    rng = np.random.default_rng(seed)
    n = 120
    X = pd.DataFrame({"a": rng.normal(size=n), "b": rng.normal(size=n)})
    pre, _cols, meta = compile_recipe(X, recipe)
    if meta["resample"] != "smote":
        raise ClassImbalanceContractError("MI-07: recipe meta must record smote resample")
    if not isinstance(pre, ImbPipeline):
        raise ClassImbalanceContractError("MI-07: smote recipe must compile to imblearn Pipeline")
    if "resample" not in pre.named_steps:
        raise ClassImbalanceContractError("MI-07: smote step missing from recipe pipeline")
    resample_cls = type(pre.named_steps["resample"]).__name__
    return {
        "mi_rule": MI07_RULE,
        "resample": "smote",
        "pipeline_class": type(pre).__name__,
        "resample_class": resample_cls,
        "seed": seed,
    }


def assert_class_imbalance_contract(*, seed: int = 42) -> list[dict[str, object]]:
    return [
        assert_mi07_imbalance_detection(seed=seed),
        assert_mi07_smote_resampler_fold_train_only(seed=seed),
        assert_mi07_recipe_wires_smote(seed=seed),
    ]


def class_imbalance_manifest(*, seed: int = 42) -> dict[str, object]:
    checks = assert_class_imbalance_contract(seed=seed)
    return {
        "id": ARTEFACT_ID,
        "stress_test": STRESS_ID,
        "mi_rule": MI07_RULE,
        "seed": seed,
        "checks": checks,
    }