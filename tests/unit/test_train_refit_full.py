"""TRAIN.REFIT.FULL — ST-FEAT-02 (oneshot-c181)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

from labcore.train.refit_full import RefitFullError, RefitFullPolicy, prepare_for_deployment
from labcore.train.refit_full_contract import ARTEFACT_ID, STRESS_ID, refit_full_manifest


def test_refit_full_manifest_seed_42() -> None:
    m = refit_full_manifest(seed=42)
    assert m["id"] == ARTEFACT_ID
    assert m["stress_test"] == STRESS_ID
    assert m["seed"] == 42
    assert m["default_enabled"] is True
    assert len(m["checks"]) == 5


def test_prepare_excludes_test() -> None:
    rng = np.random.default_rng(42)
    n = 80
    X = pd.DataFrame({"a": rng.normal(size=n), "b": rng.normal(size=n)})
    y = pd.Series((X["a"] + X["b"] > 0).astype(int))
    idx = np.arange(n)
    train_idx, test_idx = train_test_split(idx, test_size=0.25, random_state=42)
    est = LogisticRegression(max_iter=300, random_state=42).fit(
        X.iloc[train_idx], y.iloc[train_idx]
    )
    out = prepare_for_deployment(
        est, X, y, train_idx=train_idx, test_idx=test_idx, policy=RefitFullPolicy()
    )
    assert out["refit_performed"] is True
    fitted_idx = set(out["fit_indices"])
    assert fitted_idx.isdisjoint(set(int(i) for i in test_idx))
    assert out["n_fit_rows"] == n - len(test_idx)


def test_include_test_raises() -> None:
    try:
        from labcore.train.refit_full import assert_policy_allows

        assert_policy_allows(RefitFullPolicy(include_test=True))
        raise AssertionError("expected RefitFullError")
    except RefitFullError:
        pass
