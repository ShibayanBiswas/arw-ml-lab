"""Thin TS forecast metrics — libraries / simple wrappers on numpy (§19.6 subset)."""

from __future__ import annotations

from typing import Any

import numpy as np
from statsmodels.stats.diagnostic import acorr_ljungbox


def me(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.asarray(y_true, dtype=float) - np.asarray(y_pred, dtype=float)))


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(np.asarray(y_true, dtype=float) - np.asarray(y_pred, dtype=float))))


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    err = np.asarray(y_true, dtype=float) - np.asarray(y_pred, dtype=float)
    return float(np.sqrt(np.mean(err**2)))


def mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    mask = np.abs(y_true) > 0
    if not np.any(mask):
        return float("nan")
    return float(100.0 * np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])))


def wape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    denom = np.sum(np.abs(y_true))
    if denom == 0:
        return float("nan")
    return float(np.sum(np.abs(y_true - y_pred)) / denom)


def smape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    denom = np.abs(y_true) + np.abs(y_pred)
    mask = denom > 0
    if not np.any(mask):
        return float("nan")
    return float(200.0 * np.mean(np.abs(y_true[mask] - y_pred[mask]) / denom[mask]))


def directional_accuracy(y_true: np.ndarray, y_pred: np.ndarray, y_prev: np.ndarray) -> float:
    """Share of steps where sign(Δy) matches sign(ŷ − y_prev)."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    y_prev = np.asarray(y_prev, dtype=float)
    if len(y_true) == 0:
        return float("nan")
    actual = np.sign(y_true - y_prev)
    forecast = np.sign(y_pred - y_prev)
    return float(np.mean(actual == forecast))


def theil_u2(y_true: np.ndarray, y_pred: np.ndarray, y_prev: np.ndarray) -> float:
    """Theil's U2 vs naive no-change forecast."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    y_prev = np.asarray(y_prev, dtype=float)
    num = np.sqrt(np.mean((y_pred - y_true) ** 2))
    den = np.sqrt(np.mean((y_true - y_prev) ** 2))
    if den == 0 or not np.isfinite(den):
        return float("nan")
    return float(num / den)


def mase(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_train: np.ndarray,
    *,
    m: int = 1,
) -> float:
    """MASE vs seasonal naive scale on the training series (Hyndman)."""
    y_train = np.asarray(y_train, dtype=float)
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    if len(y_train) <= m:
        return float("nan")
    scale = np.mean(np.abs(y_train[m:] - y_train[:-m]))
    if scale == 0 or not np.isfinite(scale):
        return float("nan")
    return float(np.mean(np.abs(y_true - y_pred)) / scale)


def point_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_train: np.ndarray,
    *,
    m: int = 1,
) -> dict[str, float]:
    y_true_a = np.asarray(y_true, dtype=float)
    y_pred_a = np.asarray(y_pred, dtype=float)
    y_train_a = np.asarray(y_train, dtype=float)
    y_prev = np.full(len(y_true_a), y_train_a[-1]) if len(y_train_a) else np.zeros(len(y_true_a))
    return {
        "me": me(y_true_a, y_pred_a),
        "mae": mae(y_true_a, y_pred_a),
        "rmse": rmse(y_true_a, y_pred_a),
        "mape": mape(y_true_a, y_pred_a),
        "wape": wape(y_true_a, y_pred_a),
        "smape": smape(y_true_a, y_pred_a),
        "mase": mase(y_true_a, y_pred_a, y_train_a, m=m),
        "directional_accuracy": directional_accuracy(y_true_a, y_pred_a, y_prev),
        "theil_u2": theil_u2(y_true_a, y_pred_a, y_prev),
    }


def ljung_box_residuals(
    resid: np.ndarray,
    *,
    lags: int = 24,
    season_m: int = 12,
) -> dict[str, Any]:
    """Ljung-Box on residuals; report p-value at min(lags, n/5, season-aware)."""
    r = np.asarray(resid, dtype=float)
    r = r[np.isfinite(r)]
    n = len(r)
    if n < 10:
        return {
            "statistic": float("nan"),
            "pvalue": float("nan"),
            "lags": 0,
            "verdict": "not computed",
        }
    use_lags = int(min(lags, max(1, n // 5), max(season_m, 1) * 2))
    df = acorr_ljungbox(r, lags=[use_lags], return_df=True)
    stat = float(df["lb_stat"].iloc[-1])
    pval = float(df["lb_pvalue"].iloc[-1])
    return {
        "statistic": stat,
        "pvalue": pval,
        "lags": use_lags,
        "verdict": "no_autocorr" if pval > 0.05 else "autocorr",
    }
