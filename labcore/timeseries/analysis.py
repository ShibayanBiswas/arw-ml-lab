"""Thin TS analysis — classical decompose + STL + ACF/PACF numbers (§19.1 subset)."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import STL, seasonal_decompose
from statsmodels.tsa.stattools import acf, pacf


def analyse_series(
    y: pd.Series | np.ndarray,
    *,
    m: int = 12,
    nlags: int = 36,
) -> dict[str, Any]:
    y_arr = np.asarray(pd.Series(y).astype(float).to_numpy(), dtype=float)
    n = len(y_arr)
    out: dict[str, Any] = {"n": n, "m": m, "seed": 42}

    if n >= 2 * m:
        try:
            classical = seasonal_decompose(
                y_arr, model="multiplicative", period=m, extrapolate_trend="period"
            )
            out["classical"] = {
                "model": "multiplicative",
                "trend_tail": classical.trend[~np.isnan(classical.trend)][-5:].tolist(),
                "seasonal_head": classical.seasonal[:m].tolist(),
            }
        except Exception as exc:  # noqa: BLE001
            out["classical"] = {"error": str(exc)}
        try:
            stl = STL(y_arr, period=m, robust=True)
            res = stl.fit()
            out["stl"] = {
                "trend_tail": res.trend[-5:].tolist(),
                "seasonal_strength": float(
                    max(0.0, 1.0 - np.var(res.resid) / np.var(res.trend + res.resid))
                )
                if np.var(res.trend + res.resid) > 0
                else float("nan"),
            }
        except Exception as exc:  # noqa: BLE001
            out["stl"] = {"error": str(exc)}
    else:
        out["classical"] = {"error": "n < 2m"}
        out["stl"] = {"error": "n < 2m"}

    use_lags = int(min(nlags, max(1, n // 2 - 1)))
    out["acf"] = acf(y_arr, nlags=use_lags, fft=True).tolist()
    out["pacf"] = pacf(y_arr, nlags=use_lags, method="ywm").tolist()
    return out
