"""MI.SAMPLE.SIZE — ST-ML-05 MI-07/08/09 offline (oneshot-c163)."""

from __future__ import annotations

import numpy as np
import pytest

from labcore.integrity.sample_size_policy import (
    cv_scheme_for_n,
    eligible_algorithms,
    estimate_training_memory_bytes,
    memory_enqueue_decision,
    classify_class_imbalance,
)
from labcore.integrity.small_large_data_contract import (
    ARTEFACT_ID,
    SmallLargeDataContractError,
    assert_small_large_data_contract,
    assert_mi09_memory_refusal,
    small_large_data_manifest,
)
from labcore.registry.spec import AlgorithmSpec


def test_repo_small_large_contract() -> None:
    checks = assert_small_large_data_contract(seed=42)
    assert len(checks) == 4


def test_cv_scheme_for_n_mi08() -> None:
    assert cv_scheme_for_n(25, "binary") == "leave_one_out"
    assert cv_scheme_for_n(100, "binary") == "repeated_stratified_kfold"
    assert cv_scheme_for_n(100, "regression") == "repeated_kfold"
    assert cv_scheme_for_n(250, "regression") == "kfold"


def test_classify_imbalance_mi07() -> None:
    skew = classify_class_imbalance([0] * 85 + [1] * 15)
    assert skew["imbalanced"] is True
    assert skew["minority_share"] == pytest.approx(0.15)
    rare = classify_class_imbalance([0] * 28 + [1] * 2)
    assert rare["extreme_rarity"] is True


def test_eligible_algorithms_min_rows() -> None:
    spec = AlgorithmSpec(
        id="X",
        key="x.test",
        family="regression",
        name="X",
        library="sklearn",
        estimator="sklearn.linear_model.LinearRegression",
        min_rows=200,
        edu_key="x",
    )
    eligible, disabled = eligible_algorithms(50, [spec])
    assert eligible == [] and disabled[0]["key"] == "x.test"


def test_memory_refusal_mi09() -> None:
    assert_mi09_memory_refusal(seed=42)
    small = estimate_training_memory_bytes(100, 10, model_factor=1.0)
    assert memory_enqueue_decision(small, 10_000_000)["allowed"] is True
    huge = estimate_training_memory_bytes(1_000_000, 500, model_factor=4.0)
    deny = memory_enqueue_decision(huge, 50_000_000)
    assert deny["refused"] is True
    assert "refuse" in deny["message"]


def test_manifest_seed_42() -> None:
    manifest = small_large_data_manifest(seed=42)
    assert manifest["id"] == ARTEFACT_ID
    assert manifest["stress_test"] == "ST-ML-05"
    assert manifest["seed"] == 42


def test_mi09_rejects_bad_estimator(monkeypatch: pytest.MonkeyPatch) -> None:
    import labcore.integrity.small_large_data_contract as mod

    def bad_est(*_a: object, **_k: object) -> int:
        return 0

    monkeypatch.setattr(mod, "estimate_training_memory_bytes", bad_est)
    with pytest.raises(SmallLargeDataContractError, match="MI-09"):
        mod.assert_mi09_memory_refusal(seed=42)