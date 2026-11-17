"""MI.NESTED.CV — ST-ML-02 / MI-03 nested CV default (oneshot-c159)."""

from __future__ import annotations

import pandas as pd

from labcore.cv.schemes import nested_default
from labcore.integrity.nested_cv_contract import (
    ARTEFACT_ID,
    NESTED_CV_AUTO_THRESHOLD,
    build_nested_cv_manifest,
)
from labcore.train.run import TrainConfig, run_supervised_cv


def test_nested_default_threshold():
    assert NESTED_CV_AUTO_THRESHOLD == 2000
    assert nested_default(1999) is True
    assert nested_default(2000) is False


def test_manifest_auto_vs_override():
    auto = build_nested_cv_manifest(
        n_train=500,
        nested_enabled=True,
        cv_scheme="stratified_kfold",
        nested_override=None,
        seed=42,
    )
    assert auto["id"] == ARTEFACT_ID
    assert auto["source"] == "mi03_auto"
    assert auto["auto_default"] is True

    off = build_nested_cv_manifest(
        n_train=500,
        nested_enabled=False,
        cv_scheme="stratified_kfold",
        nested_override=False,
        seed=42,
    )
    assert off["source"] == "user_override"
    assert off["nested_enabled"] is False


def test_run_supervised_cv_emits_nested_cv_manifest():
    rng = __import__("numpy").random.default_rng(42)
    n = 120
    df = pd.DataFrame(
        {
            "x1": rng.normal(size=n),
            "x2": rng.normal(size=n),
            "y": rng.integers(0, 2, size=n),
        }
    )
    cfg = TrainConfig(target="y", task="binary", dataset_id="SYN-NESTED", algorithm_keys=["clf.logistic"])
    out = run_supervised_cv(df, cfg, spy_fit_counts={})
    nc = out["nested_cv"]
    assert nc["id"] == ARTEFACT_ID
    assert nc["n_train"] == 96  # 80% of 120
    assert nc["nested_enabled"] is True
    assert nc["seed"] == 42