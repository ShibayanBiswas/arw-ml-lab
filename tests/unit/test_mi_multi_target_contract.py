"""MI.MULTI.TARGET — ST-ML-02 MI-13 offline (oneshot-c174)."""

from __future__ import annotations

import numpy as np
import pytest
from sklearn.linear_model import Ridge

from labcore.integrity.multi_target_contract import (
    ARTEFACT_ID,
    MultiTargetContractError,
    assert_mi13_multioutput_regressor,
    assert_multi_target_contract,
    multi_target_manifest,
)
from labcore.integrity.multi_target_policy import (
    wrap_multioutput_regressor,
)


def test_multi_target_contract_bundle() -> None:
    checks = assert_multi_target_contract(seed=42)
    assert len(checks) == 4


def test_mi13_multioutput_regressor() -> None:
    out = assert_mi13_multioutput_regressor(seed=42)
    assert out["mi_rule"] == "MI-13"
    assert out["wrapper"] == "MultiOutputRegressor"
    assert len(out["per_target_r2"]) == 2


def test_manifest_seed_42() -> None:
    manifest = multi_target_manifest(seed=42)
    assert manifest["id"] == ARTEFACT_ID
    assert manifest["seed"] == 42
    assert manifest["stress_test"] == "ST-ML-02"
    assert manifest["mi_rule"] == "MI-13"


def test_mi13_negative_bad_shape(monkeypatch: pytest.MonkeyPatch) -> None:
    import labcore.integrity.multi_target_contract as mod

    class BadModel:
        def fit(self, *_a, **_k):
            return self

        def predict(self, X):
            return np.zeros((len(X), 1))

    def fake_wrap(_est):
        return BadModel()

    monkeypatch.setattr(mod, "wrap_multioutput_regressor", fake_wrap)
    with pytest.raises(MultiTargetContractError, match="MI-13"):
        mod.assert_mi13_multioutput_regressor(seed=42)


def test_wrap_multioutput_regressor_runs() -> None:
    rng = np.random.default_rng(42)
    X = rng.normal(size=(40, 3))
    y = rng.normal(size=(40, 2))
    model = wrap_multioutput_regressor(Ridge(random_state=42))
    model.fit(X, y)
    pred = model.predict(X)
    assert pred.shape == (40, 2)