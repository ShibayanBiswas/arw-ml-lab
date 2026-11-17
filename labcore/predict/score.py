"""Thin prediction — never refits; uses the saved pipeline only (§45 / §46)."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from labcore.predict.humility import (
    HumilityPolicy,
    apply_humility_row,
    suppress_prediction_if_abstain,
)

_POLICY_KEYS = frozenset(HumilityPolicy.__dataclass_fields__)


def _policy_from_options(humility: dict[str, Any] | HumilityPolicy) -> HumilityPolicy:
    if isinstance(humility, HumilityPolicy):
        return humility
    kwargs = {k: v for k, v in humility.items() if k in _POLICY_KEYS}
    return HumilityPolicy(**kwargs)


def predict_single(
    pipeline: Any,
    row: dict[str, Any] | pd.Series | pd.DataFrame,
    *,
    feature_names: list[str] | None = None,
    humility: dict[str, Any] | HumilityPolicy | None = None,
) -> dict[str, Any]:
    """Score one row with a fitted pipeline. Never calls fit."""
    if isinstance(row, pd.DataFrame):
        X = row
    elif isinstance(row, pd.Series):
        X = row.to_frame().T
    else:
        X = pd.DataFrame([row])
    if feature_names is not None:
        missing = [c for c in feature_names if c not in X.columns]
        if missing:
            raise ValueError(f"missing features: {missing}")
        X = X[feature_names]
    y_hat = np.asarray(pipeline.predict(X))
    pred = y_hat[0].item() if hasattr(y_hat[0], "item") else y_hat[0]
    out: dict[str, Any] = {
        "prediction": pred,
        "n_rows": 1,
        "refit": False,
    }
    if hasattr(pipeline, "predict_proba"):
        try:
            proba = np.asarray(pipeline.predict_proba(X))
            out["probabilities"] = proba[0].tolist()
        except Exception:
            pass
    if humility is not None:
        pol = _policy_from_options(humility)
        opts = humility if isinstance(humility, dict) else {}
        h = apply_humility_row(
            ood_score=float(opts.get("ood_score", 0.0)),
            flag_ood=opts.get("flag_ood"),
            flag_out_of_range=list(opts.get("flag_out_of_range") or []),
            interval_lower=opts.get("interval_lower"),
            interval_upper=opts.get("interval_upper"),
            training_target_scale=opts.get("training_target_scale"),
            policy=pol,
        )
        out["humility"] = h
        out["prediction"] = suppress_prediction_if_abstain(pred, h)
    return out


def predict_batch(
    pipeline: Any,
    X: pd.DataFrame,
    *,
    feature_names: list[str] | None = None,
) -> dict[str, Any]:
    """Score a batch; never refits."""
    frame = X[feature_names] if feature_names is not None else X
    y_hat = np.asarray(pipeline.predict(frame))
    out: dict[str, Any] = {
        "predictions": y_hat.tolist(),
        "n_rows": int(len(frame)),
        "refit": False,
    }
    if hasattr(pipeline, "predict_proba"):
        try:
            proba = np.asarray(pipeline.predict_proba(frame))
            out["probabilities"] = proba.tolist()
        except Exception:
            pass
    return out
