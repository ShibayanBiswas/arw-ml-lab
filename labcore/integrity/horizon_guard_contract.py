"""Forecast horizon caps — MI-17 / ST-ML-02 (ARCHITECTURE §46.1, §20)."""

from __future__ import annotations

from labcore.integrity.horizon_guard_policy import (
    LAB_DEFAULT_SEED,
    MI17_RULE,
    horizon_reject_reasons,
    horizon_request_allowed,
)
from labcore.timeseries.horizon_guard import compute_horizon_guard

ARTEFACT_ID = "MI.HORIZON.GUARD"
STRESS_ID = "ST-ML-02"


class HorizonGuardContractError(ValueError):
    """Raised when MI-17 offline kit contract is violated."""


def assert_mi17_ds22_h_max_fixture(*, seed: int = LAB_DEFAULT_SEED) -> dict[str, object]:
    """MI-17: DS22-style monthly series yields h_max=24 at n=144, W=4."""
    guard = compute_horizon_guard(144, "MS", m=12, w=4)
    h_max = int(guard["h_max"])
    if h_max != 24:
        raise HorizonGuardContractError(f"MI-17: DS22 fixture h_max expected 24, got {h_max}")
    _ = seed
    return {
        "mi_rule": MI17_RULE,
        "n": 144,
        "freq": "MS",
        "h_max": h_max,
        "seed": seed,
    }


def assert_mi17_rejects_over_h_max(*, seed: int = LAB_DEFAULT_SEED) -> dict[str, object]:
    """MI-17 / PV13: batch h above h_max is rejected with explicit reasons."""
    h_request = 100
    if horizon_request_allowed(144, "MS", h_request, m=12, w=4):
        raise HorizonGuardContractError("MI-17: h_request=100 must exceed h_max=24 on DS22 fixture")
    reasons = horizon_reject_reasons(144, "MS", h_request, m=12, w=4)
    if not reasons or not any("h_request" in r for r in reasons):
        raise HorizonGuardContractError("MI-17: reject_reasons must cite h_request vs h_max")
    _ = seed
    return {
        "mi_rule": MI17_RULE,
        "h_request": h_request,
        "h_max": 24,
        "request_allowed": False,
        "reject_reasons": reasons,
        "seed": seed,
    }


def assert_mi17_allows_in_range(*, seed: int = LAB_DEFAULT_SEED) -> dict[str, object]:
    """MI-17: h at h_max is allowed on the same fixture."""
    h_request = 12
    if not horizon_request_allowed(144, "MS", h_request, m=12, w=4):
        raise HorizonGuardContractError("MI-17: h_request=12 must be allowed when h_max=24")
    _ = seed
    return {
        "mi_rule": MI17_RULE,
        "h_request": h_request,
        "request_allowed": True,
        "seed": seed,
    }


def assert_mi17_small_n_cap(*, seed: int = LAB_DEFAULT_SEED) -> dict[str, object]:
    """MI-17: n<50 applies n/4 hard fraction cap (also MI-08 overlap)."""
    guard = compute_horizon_guard(40, "D", h_request=20)
    cap = max(1, 40 // 4)
    h_max = int(guard["h_max"])
    if h_max > cap:
        raise HorizonGuardContractError(f"MI-17: n=40 h_max must be ≤ n/4={cap}, got {h_max}")
    if horizon_request_allowed(40, "D", h_max + 1, w=4):
        raise HorizonGuardContractError("MI-17: h above small-n cap must be rejected")
    _ = seed
    return {
        "mi_rule": MI17_RULE,
        "n": 40,
        "h_max": h_max,
        "n_over_4_cap": cap,
        "seed": seed,
    }


def assert_horizon_guard_contract(*, seed: int = LAB_DEFAULT_SEED) -> list[dict[str, object]]:
    return [
        assert_mi17_ds22_h_max_fixture(seed=seed),
        assert_mi17_allows_in_range(seed=seed),
        assert_mi17_rejects_over_h_max(seed=seed),
        assert_mi17_small_n_cap(seed=seed),
    ]


def horizon_guard_manifest(*, seed: int = LAB_DEFAULT_SEED) -> dict[str, object]:
    checks = assert_horizon_guard_contract(seed=seed)
    return {
        "id": ARTEFACT_ID,
        "stress_test": STRESS_ID,
        "mi_rule": MI17_RULE,
        "seed": seed,
        "checks": checks,
    }