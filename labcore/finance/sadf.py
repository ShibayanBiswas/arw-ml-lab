"""Supremum ADF bubble diagnostics (Phillips–Shi–Yu, 2015) — statsmodels ADF supremum."""

from __future__ import annotations

from typing import Any, Literal

import numpy as np

RegressionMode = Literal["c", "ct", "ctt", "n"]


def _adf_statistic(
    segment: np.ndarray,
    *,
    maxlag: int,
    regression: RegressionMode,
) -> float | None:
    from statsmodels.tsa.stattools import adfuller

    try:
        res = adfuller(
            segment,
            maxlag=maxlag,
            autolag=None,
            regression=regression,
            result_object=True,
        )
        return float(res.statistic)
    except Exception:
        return None


def compute_sadf_series(
    log_prices: np.ndarray,
    *,
    min_window: int = 30,
    max_lookback: int = 60,
    maxlag: int = 0,
    regression: RegressionMode = "c",
    end_step: int = 1,
) -> dict[str, Any]:
    """
    Backward supremum ADF (SADF) series over expanding end dates.

    Phillips, Shi & Yu (2015) Testing for Multiple Bubbles. Thin wrapper over
    ``statsmodels.tsa.stattools.adfuller``; ``max_lookback`` caps inner start
    search for long series (informational plot lane until TradingLab ``get_sadf``).
    """
    if min_window < 10:
        raise ValueError("min_window must be ≥10")
    if max_lookback < min_window:
        raise ValueError("max_lookback must be ≥ min_window")
    if end_step < 1:
        raise ValueError("end_step must be ≥1")

    s = np.asarray(log_prices, dtype=float).ravel()
    s = s[np.isfinite(s)]
    n = len(s)
    if n < min_window + 5:
        raise ValueError("need ≥ min_window+5 finite log prices")

    end_indices: list[int] = []
    sadf_values: list[float] = []
    for t2 in range(min_window, n, end_step):
        t1_lo = max(0, t2 - max_lookback + 1)
        best = -np.inf
        for t1 in range(t1_lo, t2 - min_window + 2):
            seg = s[t1 : t2 + 1]
            adf = _adf_statistic(seg, maxlag=maxlag, regression=regression)
            if adf is not None and adf > best:
                best = adf
        if best > -np.inf:
            end_indices.append(t2)
            sadf_values.append(float(best))

    if not sadf_values:
        raise ValueError("SADF could not be computed on this series")

    arr = np.asarray(sadf_values, dtype=float)
    peak_i = int(np.argmax(arr))
    return {
        "end_indices": end_indices,
        "sadf": sadf_values,
        "peak_index": peak_i,
        "peak_end": int(end_indices[peak_i]),
        "peak_sadf": float(arr[peak_i]),
        "min_window": min_window,
        "max_lookback": max_lookback,
        "maxlag": maxlag,
        "regression": regression,
        "end_step": end_step,
        "n_obs": int(n),
    }