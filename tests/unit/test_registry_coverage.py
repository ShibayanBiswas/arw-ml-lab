"""Expanded §12 specs construct through build_estimator at seed 42."""

from __future__ import annotations

from typing import Any

from labcore.registry.algorithms import build_estimator, thin_algorithm_specs
from labcore.registry.algorithms_extra import COMPOSITE_KEYS, expanded_algorithm_specs

_ALLOWED = frozenset({"sklearn", "xgboost", "lightgbm", "catboost"})


def _seed_slots(est: Any) -> list[tuple[str, Any]]:
    params = est.get_params(deep=True)
    return [
        (key, val)
        for key, val in params.items()
        if key == "random_state" or key.endswith("__random_state") or key.endswith("__random_seed")
    ]


def test_expanded_specs_build_with_seed_42() -> None:
    expanded = expanded_algorithm_specs()
    assert expanded
    wired = thin_algorithm_specs()
    by_key = {spec.key: spec for spec in wired}
    assert len(by_key) == len(wired)
    assert len({spec.id for spec in wired}) == len(wired)

    for spec in expanded:
        assert spec.library in _ALLOWED
        assert spec.key in by_key
        assert by_key[spec.key].estimator == spec.estimator
        if "composite" in spec.tags:
            assert spec.key in COMPOSITE_KEYS
        override = (
            {"random_state": 42} if any(p.name == "random_state" for p in spec.params) else None
        )
        est = build_estimator(spec, override)
        assert est is not None
        seeds = _seed_slots(est)
        if any(p.name == "random_state" for p in spec.params):
            assert seeds, spec.key
            assert all(val == 42 for _, val in seeds), (spec.key, seeds)

    assert {spec.key for spec in expanded} >= COMPOSITE_KEYS
