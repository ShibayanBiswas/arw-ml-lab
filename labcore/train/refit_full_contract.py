"""Offline artefact TRAIN.REFIT.FULL — ST-FEAT-02."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

from labcore.train.refit_full import (
    ARTEFACT_ID,
    STRESS_ID,
    RefitFullError,
    RefitFullPolicy,
    prepare_for_deployment,
    refit_on_full_data,
    resolve_refit_indices,
)


class RefitFullContractError(ValueError):
    """Raised when TRAIN.REFIT.FULL contract fails."""


def assert_default_enabled() -> dict[str, object]:
    pol = RefitFullPolicy()
    if not pol.enabled:
        raise RefitFullContractError("default must be enabled (AutoGluon refit_full)")
    if pol.include_test:
        raise RefitFullContractError("include_test must default False")
    return {"enabled_default": True, "include_test": False}


def assert_include_test_forbidden() -> dict[str, object]:
    try:
        RefitFullPolicy(include_test=True)
        # dataclass allows construction; assert_policy_allows must reject
        from labcore.train.refit_full import assert_policy_allows

        assert_policy_allows(RefitFullPolicy(include_test=True))
        raise RefitFullContractError("include_test must raise")
    except RefitFullError:
        return {"include_test_rejected": True}
    raise RefitFullContractError("expected RefitFullError")


def assert_test_excluded(*, seed: int = 42) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    n = 100
    X = pd.DataFrame({"a": rng.normal(size=n), "b": rng.normal(size=n)})
    y = pd.Series((X["a"] > 0).astype(int))
    idx = np.arange(n)
    train_idx, test_idx = train_test_split(idx, test_size=0.2, random_state=seed)
    pol = RefitFullPolicy(enabled=True, scope="train_plus_oof_pool")
    resolved = resolve_refit_indices(
        n_rows=n, train_idx=train_idx, test_idx=test_idx, policy=pol
    )
    test_set = set(int(i) for i in test_idx)
    if any(int(i) in test_set for i in resolved):
        raise RefitFullContractError("test rows in refit indices")
    if len(resolved) != n - len(test_idx):
        raise RefitFullContractError("expected all non-test rows")
    est = LogisticRegression(max_iter=300, random_state=seed)
    # Fit a throwaway first so clone has same params
    est.fit(X.iloc[train_idx], y.iloc[train_idx])
    out = prepare_for_deployment(
        est, X, y, train_idx=train_idx, test_idx=test_idx, policy=pol
    )
    if not out["refit_performed"]:
        raise RefitFullContractError("refit must run when enabled")
    if out["n_fit_rows"] != len(resolved):
        raise RefitFullContractError("n_fit_rows mismatch")
    return {
        "n_fit_rows": out["n_fit_rows"],
        "n_excluded_test": out["n_excluded_test"],
        "seed": seed,
    }


def assert_toggle_off_skips(*, seed: int = 42) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    X = pd.DataFrame({"x": rng.normal(size=40)})
    y = pd.Series((X["x"] > 0).astype(int))
    est = LogisticRegression(max_iter=200, random_state=seed).fit(X, y)
    out = refit_on_full_data(est, X, y, policy=RefitFullPolicy(enabled=False))
    if out["refit_performed"]:
        raise RefitFullContractError("disabled policy must skip refit")
    if out["estimator"] is not est:
        raise RefitFullContractError("skip must return original estimator ref")
    return {"refit_performed": False, "seed": seed}


def assert_train_only_scope(*, seed: int = 42) -> dict[str, object]:
    n = 50
    train_idx = np.arange(0, 40)
    test_idx = np.arange(40, 50)
    pol = RefitFullPolicy(enabled=True, scope="train_only")
    resolved = resolve_refit_indices(
        n_rows=n, train_idx=train_idx, test_idx=test_idx, policy=pol
    )
    if not np.array_equal(resolved, train_idx):
        raise RefitFullContractError("train_only must equal train_idx")
    return {"scope": "train_only", "n": int(len(resolved)), "seed": seed}


def assert_refit_full_contract(*, seed: int = 42) -> list[dict[str, object]]:
    return [
        assert_default_enabled(),
        assert_include_test_forbidden(),
        assert_test_excluded(seed=seed),
        assert_toggle_off_skips(seed=seed),
        assert_train_only_scope(seed=seed),
    ]


def refit_full_manifest(*, seed: int = 42) -> dict[str, object]:
    checks = assert_refit_full_contract(seed=seed)
    return {
        "id": ARTEFACT_ID,
        "stress_test": STRESS_ID,
        "seed": seed,
        "default_enabled": True,
        "checks": checks,
    }
