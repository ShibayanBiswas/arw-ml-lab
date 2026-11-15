"""ParamSpec / AlgorithmSpec / catalogue contracts."""

from __future__ import annotations

from labcore.registry import AlgorithmSpec, ParamSpec, get_catalog


def test_param_spec_roundtrip() -> None:
    p = ParamSpec(
        name="n_estimators",
        type="int",
        default=200,
        low=50,
        high=2000,
        help_key="param.n_estimators",
        presets={"balanced": [100, 200, 500]},
    )
    assert p.model_dump()["name"] == "n_estimators"


def test_algorithm_spec_empty_params() -> None:
    a = AlgorithmSpec(
        id="R0",
        key="reg.placeholder",
        family="regression",
        name="Placeholder",
        library="sklearn",
        estimator="sklearn.linear_model.LinearRegression",
        edu_key="algo.reg.placeholder",
    )
    assert a.params == []


def test_catalog_phase0_empty_but_typed() -> None:
    cat = get_catalog()
    dumped = cat.model_dump()
    assert dumped["algorithms"] == []
    assert "encoders" in dumped
    assert "datasets" in dumped
