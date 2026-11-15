"""Thin prediction — never refits; uses the saved pipeline only (§45 / §46)."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def predict_single(
    pipeline: Any,
    row: dict[str, Any] | pd.Series | pd.DataFrame,
    *,
    feature_names: list[str] | None = None,
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
    out: dict[str, Any] = {
        "prediction": y_hat[0].item() if hasattr(y_hat[0], "item") else y_hat[0],
        "n_rows": 1,
        "refit": False,
    }
    if hasattr(pipeline, "predict_proba"):
        try:
            proba = np.asarray(pipeline.predict_proba(X))
            out["probabilities"] = proba[0].tolist()
        except Exception:
            pass
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
