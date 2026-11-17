"""MI.PREPROCESS.FIT — ST-ML-02 MI-01 offline (oneshot-c165)."""

from __future__ import annotations

import pytest

from labcore.integrity.preprocess_fit_contract import (
    ARTEFACT_ID,
    PreprocessFitContractError,
    assert_mi01_cross_validate_spy,
    assert_mi01_prefit_full_frame_negative,
    preprocess_fit_manifest,
)
from labcore.integrity.preprocess_fit_policy import (
    MI01_RULE,
    FitIndexSpy,
    fit_indices_match_train,
    full_frame_prefit_violates_mi01,
)


def test_fit_indices_match_train_helpers():
    tr = __import__("numpy").array([2, 5, 8])
    assert fit_indices_match_train(tr, tr)
    assert not fit_indices_match_train(__import__("numpy").arange(10), tr)


def test_full_frame_prefit_heuristic():
    assert full_frame_prefit_violates_mi01(100, 100, n_splits=4)
    assert not full_frame_prefit_violates_mi01(75, 100, n_splits=4)


def test_mi01_cross_validate_spy():
    out = assert_mi01_cross_validate_spy(seed=42)
    assert out["mi_rule"] == MI01_RULE
    assert out["folds_verified"] == 4


def test_mi01_prefit_negative():
    out = assert_mi01_prefit_full_frame_negative(seed=42)
    assert out["prefit_violation_detected"] is True


def test_preprocess_fit_manifest():
    m = preprocess_fit_manifest(seed=42)
    assert m["id"] == ARTEFACT_ID
    assert m["stress_test"] == "ST-ML-02"
    assert len(m["checks"]) == 2


def test_spy_records_dataframe_index():
    import pandas as pd

    spy = FitIndexSpy()
    X = pd.DataFrame({"v": [1.0, 2.0]}, index=pd.Index([10, 20]))
    spy.fit(X)
    assert spy.fit_indices_.tolist() == [10, 20]


def test_contract_raises_on_bad_spy(monkeypatch: pytest.MonkeyPatch):
    from labcore.integrity import preprocess_fit_contract as mod

    class BadSpy(FitIndexSpy):
        def fit(self, X, y=None):
            super().fit(X, y)
            if self.fit_indices_ is not None:
                self.fit_indices_ = self.fit_indices_[:1]
            return self

    def bad_pipeline(*, seed: int):
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import StandardScaler

        return Pipeline(
            [
                ("spy", BadSpy()),
                ("scale", StandardScaler()),
                ("clf", LogisticRegression(max_iter=200, random_state=seed)),
            ]
        )

    monkeypatch.setattr(mod, "_demo_pipeline", bad_pipeline)
    with pytest.raises(PreprocessFitContractError, match="train indices"):
        mod.assert_mi01_cross_validate_spy(seed=42)