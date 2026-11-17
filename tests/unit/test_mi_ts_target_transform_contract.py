"""MI.TS.TARGET_TRANSFORM — ST-ML-02 MI-05 offline (oneshot-c167)."""

from __future__ import annotations

import numpy as np
import pytest

from labcore.integrity.ts_target_transform_contract import (
    ARTEFACT_ID,
    TsTargetTransformContractError,
    assert_mi05_full_series_fit_leaks,
    assert_mi05_last_window_matches_full_pre_holdout,
    assert_mi05_lambdas_differ_across_windows,
    ts_target_transform_manifest,
)
from labcore.integrity.ts_target_transform_policy import (
    MI05_RULE,
    fit_boxcox_lambda,
    lambdas_differ,
    make_mi05_skew_shift_fixture,
)


def test_fit_boxcox_lambda_positive_only():
    y = np.array([1.5, 2.0, 3.0])
    lam = fit_boxcox_lambda(y)
    assert np.isfinite(lam)
    with pytest.raises(ValueError, match="positive"):
        fit_boxcox_lambda(np.array([0.0, 1.0]))


def test_lambdas_differ_helper():
    assert lambdas_differ([0.1, 0.5])
    assert not lambdas_differ([0.2, 0.2])


def test_mi05_lambdas_differ_across_windows():
    out = assert_mi05_lambdas_differ_across_windows(seed=42)
    assert out["mi_rule"] == MI05_RULE
    assert out["lambdas_differ"] is True
    assert len(out["lambdas"]) >= 2


def test_mi05_last_window_matches_full_pre_holdout():
    out = assert_mi05_last_window_matches_full_pre_holdout(seed=42)
    assert out["last_window_lambda"] == out["full_pre_holdout_lambda"]


def test_mi05_full_series_leak_negative():
    out = assert_mi05_full_series_fit_leaks(seed=42)
    assert out["leak_detected"] is True
    assert out["pre_holdout_lambda"] != out["full_series_lambda"]


def test_ts_target_transform_manifest():
    m = ts_target_transform_manifest(seed=42)
    assert m["id"] == ARTEFACT_ID
    assert m["stress_test"] == "ST-ML-02"
    assert len(m["checks"]) == 3


def test_contract_raises_when_lambdas_flat(monkeypatch: pytest.MonkeyPatch):
    from labcore.integrity import ts_target_transform_contract as mod

    monkeypatch.setattr(
        mod,
        "lambdas_per_backtest_window",
        lambda *args, **kwargs: [0.33, 0.33, 0.33, 0.33],
    )
    with pytest.raises(TsTargetTransformContractError, match="differ"):
        mod.assert_mi05_lambdas_differ_across_windows(seed=42)


def test_skew_fixture_is_strictly_positive():
    y = make_mi05_skew_shift_fixture(seed=42)
    assert (y > 0).all()