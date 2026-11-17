"""Refit-on-full-data before registration — ST-FEAT-02 / §25 + §46.5.

After CV model selection, optionally refit the champion on all non-test rows
(AutoGluon ``refit_full`` / DataRobot "prepare for deployment"). Default ON.
Never reads the locked hold-out test set for selection or this refit scope
unless ``include_test`` is explicitly True (disallowed in lab policy).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal

import numpy as np
from sklearn.base import BaseEstimator, clone

ARTEFACT_ID = "TRAIN.REFIT.FULL"
STRESS_ID = "ST-FEAT-02"

RefitScope = Literal["train_only", "train_plus_oof_pool"]


@dataclass(frozen=True)
class RefitFullPolicy:
    """Toggle shown before registry write; default matches AutoGluon refit_full."""

    enabled: bool = True
    scope: RefitScope = "train_plus_oof_pool"
    include_test: bool = False  # always False in lab policy (MI hold-out lock)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class RefitFullError(ValueError):
    """Invalid refit-full policy or inputs."""


def assert_policy_allows(policy: RefitFullPolicy) -> None:
    if policy.include_test:
        raise RefitFullError(
            "ST-FEAT-02: include_test is forbidden — hold-out test stays locked (MI)"
        )


def resolve_refit_indices(
    *,
    n_rows: int,
    train_idx: np.ndarray,
    test_idx: np.ndarray | None = None,
    policy: RefitFullPolicy | None = None,
) -> np.ndarray:
    """Indices used for the deployment refit (never the test hold-out)."""
    pol = policy or RefitFullPolicy()
    assert_policy_allows(pol)
    if not pol.enabled:
        return np.asarray(train_idx, dtype=int)
    train = np.asarray(train_idx, dtype=int)
    if test_idx is None:
        return train
    test = set(int(i) for i in np.asarray(test_idx, dtype=int))
    if pol.scope == "train_only":
        return train
    # train_plus_oof_pool: all rows except locked test
    all_idx = np.arange(n_rows, dtype=int)
    return np.asarray([i for i in all_idx if i not in test], dtype=int)


def refit_on_full_data(
    estimator: BaseEstimator,
    X: Any,
    y: Any,
    *,
    indices: np.ndarray | None = None,
    policy: RefitFullPolicy | None = None,
) -> dict[str, Any]:
    """Clone + fit on deployment indices. Skips fit when policy.enabled is False.

    Returns fitted estimator metadata; never mutates the input estimator in place
    when skipping (returns the original reference with ``refit_performed=False``).
    """
    pol = policy or RefitFullPolicy()
    assert_policy_allows(pol)
    if not pol.enabled:
        return {
            "estimator": estimator,
            "refit_performed": False,
            "n_fit_rows": None,
            "policy": pol.to_dict(),
            "artefact": ARTEFACT_ID,
        }
    if indices is None:
        n = len(X)
        indices = np.arange(n, dtype=int)
    idx = np.asarray(indices, dtype=int)
    if len(idx) == 0:
        raise RefitFullError("ST-FEAT-02: empty refit index set")
    est = clone(estimator)
    if hasattr(X, "iloc"):
        X_fit = X.iloc[idx]
        y_fit = y.iloc[idx] if hasattr(y, "iloc") else np.asarray(y)[idx]
    else:
        X_fit = np.asarray(X)[idx]
        y_fit = np.asarray(y)[idx]
    est.fit(X_fit, y_fit)
    return {
        "estimator": est,
        "refit_performed": True,
        "n_fit_rows": int(len(idx)),
        "fit_indices": idx.tolist(),
        "policy": pol.to_dict(),
        "artefact": ARTEFACT_ID,
    }


def prepare_for_deployment(
    estimator: BaseEstimator,
    X: Any,
    y: Any,
    *,
    train_idx: np.ndarray,
    test_idx: np.ndarray,
    policy: RefitFullPolicy | None = None,
) -> dict[str, Any]:
    """Registry gate: resolve indices then optional full refit."""
    pol = policy or RefitFullPolicy()
    n_rows = len(X)
    idx = resolve_refit_indices(
        n_rows=n_rows, train_idx=train_idx, test_idx=test_idx, policy=pol
    )
    # Guard: test indices must not appear
    test_set = set(int(i) for i in np.asarray(test_idx, dtype=int))
    if any(int(i) in test_set for i in idx):
        raise RefitFullError("ST-FEAT-02: test indices leaked into refit set")
    result = refit_on_full_data(estimator, X, y, indices=idx, policy=pol)
    result["n_excluded_test"] = len(test_set)
    result["stress_test"] = STRESS_ID
    return result
