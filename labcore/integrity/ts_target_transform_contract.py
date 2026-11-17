"""TS target transforms per backtest window — MI-05 / ST-ML-02 (ARCHITECTURE §46.1)."""

from __future__ import annotations

from labcore.integrity.ts_target_transform_policy import (
    DEFAULT_BACKTEST_WINDOWS,
    DEFAULT_HORIZON,
    LAMBDA_ATOL,
    MI05_RULE,
    expanding_backtest_train_slices,
    fit_boxcox_lambda,
    full_pre_holdout_slice,
    lambda_close,
    lambdas_differ,
    lambdas_per_backtest_window,
    make_mi05_skew_shift_fixture,
)

ARTEFACT_ID = "MI.TS.TARGET_TRANSFORM"
STRESS_ID = "ST-ML-02"


class TsTargetTransformContractError(ValueError):
    """Raised when MI-05 offline kit contract is violated."""


def assert_mi05_lambdas_differ_across_windows(*, seed: int = 42) -> dict[str, object]:
    """MI-05: Box-Cox λ changes when the training history grows across windows."""
    y = make_mi05_skew_shift_fixture(seed=seed)
    lambdas = lambdas_per_backtest_window(
        y,
        n_windows=DEFAULT_BACKTEST_WINDOWS,
        horizon=DEFAULT_HORIZON,
    )
    if not lambdas_differ(lambdas, atol=LAMBDA_ATOL):
        raise TsTargetTransformContractError(
            "MI-05: λ must differ across backtest windows on the skew-shift fixture"
        )
    return {
        "mi_rule": MI05_RULE,
        "n_windows": DEFAULT_BACKTEST_WINDOWS,
        "horizon": DEFAULT_HORIZON,
        "lambdas": [round(lam, 6) for lam in lambdas],
        "lambdas_differ": True,
        "seed": seed,
    }


def assert_mi05_last_window_matches_full_pre_holdout(*, seed: int = 42) -> dict[str, object]:
    """MI-05: the last backtest window's train λ equals full pre-holdout history λ."""
    y = make_mi05_skew_shift_fixture(seed=seed)
    slices = expanding_backtest_train_slices(
        y,
        n_windows=DEFAULT_BACKTEST_WINDOWS,
        horizon=DEFAULT_HORIZON,
    )
    if not slices:
        raise TsTargetTransformContractError("MI-05: missing backtest train slices")
    last_lambda = fit_boxcox_lambda(slices[-1])
    full_hist = full_pre_holdout_slice(y, horizon=DEFAULT_HORIZON)
    full_lambda = fit_boxcox_lambda(full_hist)
    if not lambda_close(last_lambda, full_lambda, atol=LAMBDA_ATOL):
        raise TsTargetTransformContractError(
            "MI-05: last window λ must equal λ on full pre-holdout history"
        )
    early_lambda = fit_boxcox_lambda(slices[0])
    if lambda_close(early_lambda, full_lambda, atol=LAMBDA_ATOL):
        raise TsTargetTransformContractError(
            "MI-05: fixture requires early λ ≠ full-history λ"
        )
    return {
        "mi_rule": MI05_RULE,
        "last_window_lambda": round(last_lambda, 6),
        "full_pre_holdout_lambda": round(full_lambda, 6),
        "early_window_lambda": round(early_lambda, 6),
        "seed": seed,
    }


def assert_mi05_full_series_fit_leaks(*, seed: int = 42) -> dict[str, object]:
    """MI-05 negative: fitting λ on the entire series (incl. holdout) ≠ pre-holdout λ."""
    y = make_mi05_skew_shift_fixture(seed=seed)
    pre = fit_boxcox_lambda(full_pre_holdout_slice(y, horizon=DEFAULT_HORIZON))
    leak = fit_boxcox_lambda(y)
    if lambda_close(pre, leak, atol=LAMBDA_ATOL):
        raise TsTargetTransformContractError(
            "MI-05: full-series λ fit must differ from pre-holdout λ on fixture"
        )
    return {
        "mi_rule": MI05_RULE,
        "pre_holdout_lambda": round(pre, 6),
        "full_series_lambda": round(leak, 6),
        "leak_detected": True,
        "seed": seed,
    }


def assert_ts_target_transform_contract(*, seed: int = 42) -> list[dict[str, object]]:
    return [
        assert_mi05_lambdas_differ_across_windows(seed=seed),
        assert_mi05_last_window_matches_full_pre_holdout(seed=seed),
        assert_mi05_full_series_fit_leaks(seed=seed),
    ]


def ts_target_transform_manifest(*, seed: int = 42) -> dict[str, object]:
    checks = assert_ts_target_transform_contract(seed=seed)
    return {
        "id": ARTEFACT_ID,
        "stress_test": STRESS_ID,
        "mi_rule": MI05_RULE,
        "seed": seed,
        "checks": checks,
    }