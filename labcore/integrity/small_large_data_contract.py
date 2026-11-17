"""Small/large data integrity — MI-07 / MI-08 / MI-09 / ST-ML-05 (ARCHITECTURE §46.1)."""

from __future__ import annotations

from labcore.integrity.sample_size_policy import (
    BYTES_PER_CELL,
    DL_MIN_ROWS_DEFAULT,
    LOO_N_THRESHOLD,
    REFUSAL_OVER_LIMIT_RATIO,
    SMALL_N_REPEATED_CV,
    assert_repeated_cv_schemes_registered,
    classify_class_imbalance,
    cv_scheme_for_n,
    eligible_algorithms,
    estimate_training_memory_bytes,
    memory_enqueue_decision,
)
from labcore.registry.spec import AlgorithmSpec
from labcore.timeseries.horizon_guard import compute_horizon_guard

ARTEFACT_ID = "MI.SAMPLE.SIZE"
MI_RULES = ("MI-07", "MI-08", "MI-09")
STRESS_ID = "ST-ML-05"


class SmallLargeDataContractError(ValueError):
    """Raised when ST-ML-05 offline kit contract is violated."""


def assert_mi08_cv_scheme_ladder(*, seed: int = 42) -> dict[str, object]:
    """MI-08: LOO below 50 rows; repeated CV below 200; default otherwise."""
    _ = seed
    if cv_scheme_for_n(30, "binary") != "leave_one_out":
        raise SmallLargeDataContractError("MI-08: n<50 must use leave_one_out")
    if cv_scheme_for_n(120, "binary") != "repeated_stratified_kfold":
        raise SmallLargeDataContractError("MI-08: n<200 binary must use repeated_stratified_kfold")
    if cv_scheme_for_n(120, "regression") != "repeated_kfold":
        raise SmallLargeDataContractError("MI-08: n<200 regression must use repeated_kfold")
    if cv_scheme_for_n(500, "binary") != "stratified_kfold":
        raise SmallLargeDataContractError("MI-08: n≥200 must use default stratified_kfold")
    reg = assert_repeated_cv_schemes_registered()
    return {
        "mi_rule": "MI-08",
        "small_n_threshold": SMALL_N_REPEATED_CV,
        "loo_threshold": LOO_N_THRESHOLD,
        **reg,
        "seed": seed,
    }


def assert_mi08_min_rows_and_dl_gate(*, seed: int = 42) -> dict[str, object]:
    """MI-08: registry min_rows and DL 1k gate via ``eligible_algorithms``."""
    _ = seed
    heavy = AlgorithmSpec(
        id="SYN",
        key="syn.heavy",
        family="classification",
        name="Synthetic heavy",
        library="sklearn",
        estimator="sklearn.dummy.DummyClassifier",
        min_rows=500,
        edu_key="syn.heavy",
    )
    deep = AlgorithmSpec(
        id="SYN-DL",
        key="dl.syn",
        family="classification",
        name="Synthetic DL",
        library="pytorch-tabular",
        estimator="labcore.deep.tabular.fit_tabular",
        tags=["deep"],
        edu_key="dl.syn",
    )
    eligible, disabled = eligible_algorithms(120, [heavy, deep])
    if eligible:
        raise SmallLargeDataContractError("MI-08: expected no eligible algos at n=120")
    keys = {d["key"] for d in disabled}
    if keys != {"syn.heavy", "dl.syn"}:
        raise SmallLargeDataContractError(f"MI-08: unexpected disabled keys {keys}")
    guard = compute_horizon_guard(40, "D", h_request=20)
    cap = max(1, 40 // 4)
    if int(guard["h_max"]) > cap:
        raise SmallLargeDataContractError(
            f"MI-08: n<50 h_max must be ≤ n/4={cap}, got {guard['h_max']}",
        )
    return {
        "mi_rule": "MI-08",
        "disabled_count": len(disabled),
        "dl_min_rows": DL_MIN_ROWS_DEFAULT,
        "h_max_n40": int(guard["h_max"]),
        "seed": seed,
    }


def assert_mi07_imbalance_flags(*, seed: int = 42) -> dict[str, object]:
    """MI-07: minority share and ratio rules on a skewed label vector."""
    import numpy as np

    rng = np.random.default_rng(seed)
    y = np.array([0] * 90 + [1] * 10, dtype=int)
    info = classify_class_imbalance(y)
    if not info["imbalanced"]:
        raise SmallLargeDataContractError("MI-07: 10/100 minority must be imbalanced")
    y_rare = np.array([0] * 28 + [1] * 2, dtype=int)
    rare = classify_class_imbalance(y_rare)
    if not rare["extreme_rarity"]:
        raise SmallLargeDataContractError("MI-07: minority < 30 rows must set extreme_rarity")
    _ = rng  # seed exercised for parity with other checks
    return {
        "mi_rule": "MI-07",
        "skewed_minority_share": info["minority_share"],
        "skewed_imbalanced": info["imbalanced"],
        "seed": seed,
    }


def assert_mi09_memory_refusal(*, seed: int = 42) -> dict[str, object]:
    """MI-09: memory estimate and 1.2× refusal message with numbers."""
    _ = seed
    est_ok = estimate_training_memory_bytes(1_000, 20, model_factor=2.0)
    expected = 1_000 * 20 * BYTES_PER_CELL * 2
    if est_ok != expected:
        raise SmallLargeDataContractError(f"MI-09: expected {expected} B, got {est_ok}")
    worker_limit = 500_000
    ok = memory_enqueue_decision(est_ok, worker_limit)
    if not ok["allowed"]:
        raise SmallLargeDataContractError("MI-09: small job should be allowed")
    big = estimate_training_memory_bytes(200_000, 200, model_factor=3.0)
    bad = memory_enqueue_decision(big, 50_000_000)
    if not bad["refused"]:
        raise SmallLargeDataContractError("MI-09: large job must hit refusal threshold")
    if str(REFUSAL_OVER_LIMIT_RATIO) not in bad["message"] and "1.2" not in bad["message"]:
        raise SmallLargeDataContractError("MI-09: refusal must cite limit ratio")
    if str(big) not in bad["message"]:
        raise SmallLargeDataContractError("MI-09: refusal must include estimated bytes")
    return {
        "mi_rule": "MI-09",
        "estimate_ok_bytes": est_ok,
        "estimate_refused_bytes": big,
        "refusal_ratio": REFUSAL_OVER_LIMIT_RATIO,
        "seed": seed,
    }


def assert_small_large_data_contract(*, seed: int = 42) -> list[dict[str, object]]:
    """Run all ST-ML-05 offline checks."""
    return [
        assert_mi07_imbalance_flags(seed=seed),
        assert_mi08_cv_scheme_ladder(seed=seed),
        assert_mi08_min_rows_and_dl_gate(seed=seed),
        assert_mi09_memory_refusal(seed=seed),
    ]


def small_large_data_manifest(*, seed: int = 42) -> dict[str, object]:
    checks = assert_small_large_data_contract(seed=seed)
    return {
        "id": ARTEFACT_ID,
        "stress_test": STRESS_ID,
        "mi_rules": list(MI_RULES),
        "seed": seed,
        "checks": checks,
    }