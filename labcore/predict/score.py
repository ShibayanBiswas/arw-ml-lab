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


def _level_tag(confidence_level: float) -> str:
    pct = int(round(float(confidence_level) * 100))
    return str(pct)


def try_predict_intervals(
    pipeline: Any,
    X: pd.DataFrame,
    *,
    confidence_level: float = 0.9,
) -> dict[str, Any] | None:
    """Return lower/upper arrays when the saved object exposes intervals (never refits).

    Supports MAPIE-style ``predict_interval`` and a stored residual quantile
    ``conformal_qhat_`` (split-conformal absolute residual).
    """
    level = float(confidence_level)
    tag = _level_tag(level)

    if hasattr(pipeline, "predict_interval"):
        try:
            y_pred, y_pis = pipeline.predict_interval(X)
            pis = np.asarray(y_pis)
            if pis.ndim == 3:
                lower = pis[:, 0, 0]
                upper = pis[:, 1, 0]
            elif pis.ndim == 2 and pis.shape[1] >= 2:
                lower = pis[:, 0]
                upper = pis[:, 1]
            else:
                return None
            return {
                "pred_lower": np.asarray(lower, dtype=float).ravel().tolist(),
                "pred_upper": np.asarray(upper, dtype=float).ravel().tolist(),
                "pred_interval_method": "mapie_predict_interval",
                "confidence_level": level,
                "level_tag": tag,
                "y_pred": np.asarray(y_pred).ravel().tolist(),
            }
        except Exception:
            pass

    qhat = getattr(pipeline, "conformal_qhat_", None)
    if qhat is not None:
        try:
            y_hat = np.asarray(pipeline.predict(X), dtype=float).ravel()
            q = float(qhat)
            return {
                "pred_lower": (y_hat - q).tolist(),
                "pred_upper": (y_hat + q).tolist(),
                "pred_interval_method": "split_conformal_residual",
                "confidence_level": level,
                "level_tag": tag,
                "y_pred": y_hat.tolist(),
            }
        except Exception:
            return None
    return None


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
    confidence_level: float = 0.9,
) -> dict[str, Any]:
    """Score a batch; never refits. Adds conformal interval columns when available."""
    frame = X[feature_names] if feature_names is not None else X
    y_hat = np.asarray(pipeline.predict(frame))
    out: dict[str, Any] = {
        "predictions": y_hat.tolist(),
        "n_rows": int(len(frame)),
        "refit": False,
    }
    if hasattr(pipeline, "predict_proba"):
        try:
            proba = np.asarray(pipeline.predict_proba(frame), dtype=float)
            out["probabilities"] = proba.tolist()
            # §45.4 classification columns (from library proba; scipy entropy)
            if proba.ndim == 2 and proba.shape[1] >= 2:
                from scipy.stats import entropy as _scipy_entropy

                conf = proba.max(axis=1)
                # top-1 − top-2 margin
                part = np.partition(proba, -2, axis=1)
                margin = part[:, -1] - part[:, -2]
                # normalised entropy in [0, 1]
                h = _scipy_entropy(proba, axis=1, base=2)
                h_max = np.log2(float(proba.shape[1]))
                h_norm = h / h_max if h_max > 0 else h
                out["pred_confidence"] = conf.tolist()
                out["pred_margin"] = margin.tolist()
                out["pred_entropy"] = h_norm.tolist()
                out["classification_columns"] = [
                    "pred_confidence",
                    "pred_margin",
                    "pred_entropy",
                ]
        except Exception:
            pass
    intervals = try_predict_intervals(pipeline, frame, confidence_level=confidence_level)
    if intervals is not None:
        tag = intervals["level_tag"]
        out[f"pred_lower_{tag}"] = intervals["pred_lower"]
        out[f"pred_upper_{tag}"] = intervals["pred_upper"]
        out["pred_interval_method"] = intervals["pred_interval_method"]
        out["confidence_level"] = intervals["confidence_level"]
        out["interval_columns"] = [
            f"pred_lower_{tag}",
            f"pred_upper_{tag}",
            "pred_interval_method",
        ]
    return out
