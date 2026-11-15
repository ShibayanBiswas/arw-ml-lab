"""Phase 3 thin: TreeSHAP, PDP=mean ICE, conformal, calibration, feature contract."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from labcore.explain.shap_trees import pdp_equals_mean_ice, tree_shap_explain
from labcore.predict.contract import (
    assert_no_identifier_values,
    build_feature_contract,
    validate_feature_contract,
)
from labcore.predict.score import predict_batch, predict_single
from labcore.uncertainty.calibration import calibrate_binary
from labcore.uncertainty.conformal import split_conformal_aps, split_conformal_regression
from lightgbm import LGBMClassifier, LGBMRegressor
from sklearn.datasets import fetch_california_housing, load_breast_cancer, make_classification
from sklearn.model_selection import train_test_split


def test_feature_contract_schema_and_no_id_values():
    rng = np.random.default_rng(42)
    X = pd.DataFrame(
        {
            "age": rng.integers(18, 80, size=100),
            "income": rng.normal(50_000, 10_000, size=100),
            "user_id": [f"u{i}" for i in range(100)],
            "city": rng.choice(["A", "B", "C"], size=100),
        }
    )
    contract = build_feature_contract(X, dataset_id="SYN", task="binary", target="y", seed=42)
    errs = validate_feature_contract(contract)
    assert errs == [], errs
    assert_no_identifier_values(contract)
    id_feats = [f for f in contract["features"] if f["kind"] == "identifier_like"]
    assert id_feats and id_feats[0]["name"] == "user_id"
    assert "categories" not in id_feats[0]


def test_tree_shap_additivity_lgbm():
    X, y = load_breast_cancer(return_X_y=True, as_frame=True)
    X_tr, X_te, y_tr, _ = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    model = LGBMClassifier(n_estimators=40, max_depth=3, random_state=42, verbose=-1)
    model.fit(X_tr, y_tr)
    out = tree_shap_explain(model, X_te.iloc[:20])
    assert out["additivity_max_abs"] < 1e-6


def test_pdp_equals_mean_ice():
    X, y = load_breast_cancer(return_X_y=True, as_frame=True)
    X_tr, _, y_tr, _ = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    model = LGBMClassifier(n_estimators=30, max_depth=3, random_state=42, verbose=-1)
    model.fit(X_tr, y_tr)
    out = pdp_equals_mean_ice(model, X_tr.iloc[:80], feature=0, grid_resolution=15)
    assert out["max_abs_pdp_minus_mean_ice"] < 1e-8


def test_split_conformal_reg_coverage_ds12():
    data = fetch_california_housing(as_frame=True)
    X = data.data.to_numpy()
    y = data.target.to_numpy()
    # Full DS12 hold-out path (subsample for CI wall-time; seed 42)
    rng = np.random.default_rng(42)
    idx = rng.choice(len(X), size=4000, replace=False)
    X, y = X[idx], y[idx]
    model = LGBMRegressor(n_estimators=80, max_depth=5, random_state=42, verbose=-1)
    out = split_conformal_regression(model, X, y, confidence_level=0.9, seed=42)
    # AC: 88–92% empirical coverage at 90%
    assert 0.88 <= out["coverage"] <= 0.92, out


def test_aps_sets_coverage_multiclass():
    X, y = make_classification(
        n_samples=1200,
        n_features=12,
        n_informative=8,
        n_classes=3,
        n_clusters_per_class=1,
        random_state=42,
    )
    model = LGBMClassifier(n_estimators=40, max_depth=3, random_state=42, verbose=-1)
    out = split_conformal_aps(model, X, y, confidence_level=0.9, seed=42)
    assert out["coverage"] >= 0.89, out


def test_calibration_reduces_ece():
    # Shallow high-LR booster → overconfident raw probs; isotonic should cut ECE
    X, y = make_classification(
        n_samples=2000,
        n_features=15,
        n_informative=8,
        n_redundant=2,
        weights=[0.7, 0.3],
        random_state=42,
    )
    model = LGBMClassifier(
        n_estimators=80, max_depth=2, learning_rate=0.3, random_state=42, verbose=-1
    )
    out = calibrate_binary(model, X, y, method="isotonic", seed=42)
    assert out["ece_after"] < out["ece_before"], out
    assert out["ece_reduced"] is True


def test_predict_never_refits():
    X, y = load_breast_cancer(return_X_y=True, as_frame=True)
    X_tr, X_te, y_tr, _ = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    model = LGBMClassifier(n_estimators=20, max_depth=2, random_state=42, verbose=-1)
    model.fit(X_tr, y_tr)
    row = X_te.iloc[0].to_dict()
    one = predict_single(model, row, feature_names=list(X.columns))
    batch = predict_batch(model, X_te.iloc[:5], feature_names=list(X.columns))
    assert one["refit"] is False
    assert batch["refit"] is False
    assert "prediction" in one
    assert len(batch["predictions"]) == 5


@pytest.mark.parametrize("method", ["sigmoid", "isotonic"])
def test_calibration_methods_run(method: str):
    X, y = make_classification(n_samples=800, n_features=10, random_state=42)
    model = LGBMClassifier(n_estimators=20, max_depth=2, random_state=42, verbose=-1)
    out = calibrate_binary(model, X, y, method=method, seed=42)  # type: ignore[arg-type]
    assert np.isfinite(out["ece_before"])
    assert np.isfinite(out["ece_after"])
