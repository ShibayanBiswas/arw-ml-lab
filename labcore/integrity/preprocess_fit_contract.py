"""Preprocessing fit scope — MI-01 / ST-ML-02 (ARCHITECTURE §46.1)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from labcore.integrity.preprocess_fit_policy import (
    MI01_RULE,
    FitIndexSpy,
    fit_indices_match_train,
    full_frame_prefit_violates_mi01,
)

ARTEFACT_ID = "MI.PREPROCESS.FIT"
STRESS_ID = "ST-ML-02"


class PreprocessFitContractError(ValueError):
    """Raised when MI-01 offline kit contract is violated."""


def _demo_pipeline(*, seed: int) -> Pipeline:
    return Pipeline(
        [
            ("spy", FitIndexSpy()),
            ("scale", StandardScaler()),
            (
                "clf",
                LogisticRegression(max_iter=500, random_state=seed),
            ),
        ]
    )


def assert_mi01_cross_validate_spy(*, seed: int = 42) -> dict[str, object]:
    """MI-01: each fold's spy.fit_indices_ equals that fold's train indices."""
    rng = np.random.default_rng(seed)
    n = 200
    X = pd.DataFrame(
        {
            "a": rng.normal(size=n),
            "b": rng.normal(size=n),
        },
        index=pd.RangeIndex(0, n),
    )
    y = (X["a"] + rng.normal(scale=0.5, size=n) > 0).astype(int).to_numpy()
    pipe = _demo_pipeline(seed=seed)
    cv = KFold(n_splits=4, shuffle=True, random_state=seed)
    out = cross_validate(
        pipe,
        X,
        y,
        cv=cv,
        return_estimator=True,
        scoring="accuracy",
    )
    for est, (tr_idx, _va_idx) in zip(out["estimator"], cv.split(X)):
        spy = est.named_steps["spy"]
        if spy.fit_indices_ is None:
            raise PreprocessFitContractError("MI-01: spy missing fit_indices_")
        if not fit_indices_match_train(spy.fit_indices_, tr_idx, index=X.index):
            raise PreprocessFitContractError(
                "MI-01: spy fit indices must equal fold train indices"
            )
    return {
        "mi_rule": MI01_RULE,
        "n_rows": n,
        "n_splits": 4,
        "folds_verified": len(out["estimator"]),
        "seed": seed,
    }


def assert_mi01_prefit_full_frame_negative(*, seed: int = 42) -> dict[str, object]:
    """MI-01: fitting the pipeline on all rows before CV is flagged."""
    rng = np.random.default_rng(seed)
    n = 120
    X = pd.DataFrame({"x": rng.normal(size=n)}, index=pd.RangeIndex(0, n))
    y = rng.integers(0, 2, size=n)
    pipe = _demo_pipeline(seed=seed)
    pipe.fit(X, y)
    spy = pipe.named_steps["spy"]
    if spy.fit_indices_ is None:
        raise PreprocessFitContractError("MI-01: negative fixture missing spy indices")
    violates = full_frame_prefit_violates_mi01(len(spy.fit_indices_), n, n_splits=4)
    if not violates:
        raise PreprocessFitContractError("MI-01: full-frame prefit must violate MI-01 heuristic")
    cv = KFold(n_splits=4, shuffle=True, random_state=seed)
    tr0, _ = next(iter(cv.split(X)))
    if fit_indices_match_train(spy.fit_indices_, tr0, index=X.index):
        raise PreprocessFitContractError("MI-01: prefit spy must not match a single fold train set")
    return {
        "mi_rule": MI01_RULE,
        "n_fit_rows": int(len(spy.fit_indices_)),
        "prefit_violation_detected": True,
        "seed": seed,
    }


def assert_preprocess_fit_contract(*, seed: int = 42) -> list[dict[str, object]]:
    return [
        assert_mi01_cross_validate_spy(seed=seed),
        assert_mi01_prefit_full_frame_negative(seed=seed),
    ]


def preprocess_fit_manifest(*, seed: int = 42) -> dict[str, object]:
    checks = assert_preprocess_fit_contract(seed=seed)
    return {
        "id": ARTEFACT_ID,
        "stress_test": STRESS_ID,
        "mi_rule": MI01_RULE,
        "seed": seed,
        "checks": checks,
    }