"""PRED.HUMILITY — ST-FEAT-01 humility rules (oneshot-c180)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from labcore.predict.humility import HumilityPolicy, apply_humility_row
from labcore.predict.humility_contract import ARTEFACT_ID, STRESS_ID, humility_manifest
from labcore.predict.score import predict_single


def test_humility_manifest_seed_42() -> None:
    manifest = humility_manifest(seed=42)
    assert manifest["id"] == ARTEFACT_ID
    assert manifest["stress_test"] == STRESS_ID
    assert manifest["seed"] == 42
    assert len(manifest["checks"]) == 6
    assert set(manifest["actions"]) == {"warn", "abstain", "review"}


def test_abstain_suppresses_predict_single() -> None:
    rng = np.random.default_rng(42)
    train = pd.DataFrame(rng.normal(size=(40, 2)), columns=["f0", "f1"])
    y = (train["f0"] > 0).astype(int).to_numpy()
    clf = LogisticRegression(max_iter=200, random_state=42).fit(train, y)
    out = predict_single(
        clf,
        {"f0": float(train.iloc[0]["f0"]), "f1": float(train.iloc[0]["f1"])},
        feature_names=["f0", "f1"],
        humility={
            "ood_score": 0.0,
            "interval_lower": 0.0,
            "interval_upper": 50.0,
            "training_target_scale": 10.0,
            "action_wide_interval": "abstain",
            "interval_width_ratio_max": 1.0,
        },
    )
    assert out["refit"] is False
    assert out["humility"]["abstain"] is True
    assert out["prediction"] is None


def test_clean_predict_single_keeps_value() -> None:
    rng = np.random.default_rng(42)
    X = pd.DataFrame(rng.normal(size=(40, 2)), columns=["f0", "f1"])
    y = (X["f0"] > 0).astype(int).to_numpy()
    clf = LogisticRegression(max_iter=200, random_state=42).fit(X, y)
    out = predict_single(
        clf,
        {"f0": 0.1, "f1": -0.2},
        feature_names=["f0", "f1"],
        humility={"ood_score": 0.2},
    )
    assert out["prediction"] is not None
    assert out["humility"]["humility_action"] is None


def test_policy_review_on_oor() -> None:
    h = apply_humility_row(
        flag_out_of_range=["x"],
        policy=HumilityPolicy(action_out_of_range="review"),
    )
    assert h["needs_human_review"] is True
    assert h["humility_action"] == "review"
