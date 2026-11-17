"""Multi-target supervised integrity — MI-13 / ST-ML-02 (ARCHITECTURE §46.1)."""

from __future__ import annotations

import numpy as np
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.model_selection import train_test_split

from labcore.integrity.multi_target_policy import (
    LAB_DEFAULT_SEED,
    MI13_RULE,
    macro_mean_r2,
    per_target_r2,
    prediction_studio_column_groups,
    wrap_multilabel_classifier,
    wrap_multioutput_regressor,
    wrap_regressor_chain,
)

ARTEFACT_ID = "MI.MULTI.TARGET"
STRESS_ID = "ST-ML-02"


class MultiTargetContractError(ValueError):
    """Raised when MI-13 offline kit contract is violated."""


def _synthetic_multioutput_xy(
    *,
    seed: int,
    n: int = 160,
) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, 5))
    noise = rng.normal(scale=0.15, size=(n, 2))
    y = np.column_stack(
        [
            2.0 * X[:, 0] + 0.5 * X[:, 1] + noise[:, 0],
            -1.2 * X[:, 2] + 0.3 * X[:, 3] + noise[:, 1],
        ],
    )
    return X, y


def _synthetic_multilabel_xy(
    *,
    seed: int,
    n: int = 160,
) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, 4))
    y = np.column_stack(
        [
            (X[:, 0] > 0).astype(int),
            (X[:, 1] + X[:, 2] > 0).astype(int),
        ],
    )
    return X, y


def assert_mi13_multioutput_regressor(*, seed: int = LAB_DEFAULT_SEED) -> dict[str, object]:
    """MI-13: ``MultiOutputRegressor`` fits two targets; per-target R² reported."""
    X, y = _synthetic_multioutput_xy(seed=seed)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, random_state=seed)
    model = wrap_multioutput_regressor(Ridge(random_state=seed))
    model.fit(X_tr, y_tr)
    pred = model.predict(X_te)
    if pred.shape != y_te.shape:
        raise MultiTargetContractError(
            f"MI-13: expected pred shape {y_te.shape}, got {pred.shape}",
        )
    r2_each = per_target_r2(y_te, pred)
    if len(r2_each) != 2:
        raise MultiTargetContractError("MI-13: expected two per-target R² values")
    if not all(r > 0.5 for r in r2_each):
        raise MultiTargetContractError(
            f"MI-13: expected strong fit on synthetic data, got {r2_each}",
        )
    return {
        "mi_rule": MI13_RULE,
        "wrapper": "MultiOutputRegressor",
        "n_targets": 2,
        "per_target_r2": r2_each,
        "macro_mean_r2": macro_mean_r2(r2_each),
        "seed": seed,
    }


def assert_mi13_regressor_chain(*, seed: int = LAB_DEFAULT_SEED) -> dict[str, object]:
    """MI-13: ``RegressorChain`` with seeded chain order predicts both targets."""
    X, y = _synthetic_multioutput_xy(seed=seed)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, random_state=seed)
    model = wrap_regressor_chain(Ridge(random_state=seed), random_state=seed)
    model.fit(X_tr, y_tr)
    pred = model.predict(X_te)
    if pred.shape != y_te.shape:
        raise MultiTargetContractError("MI-13: RegressorChain pred shape mismatch")
    if not np.isfinite(pred).all():
        raise MultiTargetContractError("MI-13: RegressorChain predictions must be finite")
    return {
        "mi_rule": MI13_RULE,
        "wrapper": "RegressorChain",
        "n_targets": 2,
        "chain_random_state": seed,
        "seed": seed,
    }


def assert_mi13_multilabel_classifier(*, seed: int = LAB_DEFAULT_SEED) -> dict[str, object]:
    """MI-13: ``MultiOutputClassifier`` on two binary labels."""
    X, y = _synthetic_multilabel_xy(seed=seed)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, random_state=seed)
    base = LogisticRegression(max_iter=500, random_state=seed)
    model = wrap_multilabel_classifier(base)
    model.fit(X_tr, y_tr)
    pred = model.predict(X_te)
    if pred.shape != y_te.shape:
        raise MultiTargetContractError("MI-13: multilabel pred shape mismatch")
    acc_per_label = [(pred[:, i] == y_te[:, i]).mean() for i in range(2)]
    if not all(float(a) > 0.55 for a in acc_per_label):
        raise MultiTargetContractError(
            f"MI-13: expected label accuracy > 0.55, got {acc_per_label}",
        )
    return {
        "mi_rule": MI13_RULE,
        "wrapper": "MultiOutputClassifier",
        "n_labels": 2,
        "per_label_accuracy": [float(a) for a in acc_per_label],
        "seed": seed,
    }


def assert_mi13_prediction_studio_groups(*, seed: int = LAB_DEFAULT_SEED) -> dict[str, object]:
    """MI-13: Prediction Studio emits one column group per target name."""
    targets = ["y1", "y2"]
    groups = prediction_studio_column_groups(targets, suffix="_pred")
    if set(groups.keys()) != set(targets):
        raise MultiTargetContractError("MI-13: column groups must cover each target")
    for name in targets:
        if groups[name] != [f"{name}_pred"]:
            raise MultiTargetContractError(f"MI-13: unexpected group for {name}")
    return {
        "mi_rule": MI13_RULE,
        "targets": targets,
        "column_groups": groups,
        "seed": seed,
    }


def assert_multi_target_contract(*, seed: int = LAB_DEFAULT_SEED) -> list[dict[str, object]]:
    return [
        assert_mi13_multioutput_regressor(seed=seed),
        assert_mi13_regressor_chain(seed=seed),
        assert_mi13_multilabel_classifier(seed=seed),
        assert_mi13_prediction_studio_groups(seed=seed),
    ]


def multi_target_manifest(*, seed: int = LAB_DEFAULT_SEED) -> dict[str, object]:
    checks = assert_multi_target_contract(seed=seed)
    return {
        "id": ARTEFACT_ID,
        "stress_test": STRESS_ID,
        "mi_rule": MI13_RULE,
        "seed": seed,
        "checks": checks,
    }