"""Trend-scanning t-statistics (AFML Ch.3) — scipy ``linregress`` wrapper."""

from __future__ import annotations

from typing import Any

import numpy as np


def _slope_t_stat(segment: np.ndarray) -> float | None:
    from scipy.stats import linregress

    seg = np.asarray(segment, dtype=float).ravel()
    if len(seg) < 3 or not np.all(np.isfinite(seg)):
        return None
    x = np.arange(len(seg), dtype=float)
    res = linregress(x, seg)
    if not np.isfinite(res.stderr) or res.stderr <= 0:
        return None
    t_val = float(res.slope / res.stderr)
    return t_val if np.isfinite(t_val) else None


def compute_trendscan_series(
    log_prices: np.ndarray,
    *,
    l_min: int = 5,
    l_max: int = 20,
    step: int = 1,
) -> dict[str, Any]:
    """
    Max-|t| trend scan over forward windows L ∈ [l_min, l_max].

    López de Prado, *Advances in Financial Machine Learning*, trend-scanning
    labels: at each origin, pick the window with the largest |slope t-stat|.
    Thin wrapper over ``scipy.stats.linregress`` until TradingLab
    ``trend_scanning_labels`` is wired.
    """
    if l_min < 3:
        raise ValueError("l_min must be ≥3")
    if l_max < l_min:
        raise ValueError("l_max must be ≥ l_min")
    if step < 1:
        raise ValueError("step must be ≥1")

    s = np.asarray(log_prices, dtype=float).ravel()
    s = s[np.isfinite(s)]
    n = len(s)
    if n < l_max + 5:
        raise ValueError("need ≥ l_max+5 finite log prices")

    origins: list[int] = []
    t_values: list[float]
    t_values = []
    best_lens: list[int] = []
    last_origin = n - l_max

    for t0 in range(0, last_origin + 1, step):
        best_t: float | None = None
        best_l = l_min
        for length in range(l_min, l_max + 1):
            seg = s[t0 : t0 + length]
            t_stat = _slope_t_stat(seg)
            if t_stat is None:
                continue
            if best_t is None or abs(t_stat) > abs(best_t):
                best_t = t_stat
                best_l = length
        if best_t is None:
            continue
        origins.append(t0)
        t_values.append(float(best_t))
        best_lens.append(int(best_l))

    if not t_values:
        raise ValueError("trend-scan t-values could not be computed on this series")

    arr = np.asarray(t_values, dtype=float)
    peak_i = int(np.argmax(np.abs(arr)))
    significant = float(np.mean(np.abs(arr) > 2.0))
    return {
        "origins": origins,
        "t_value": t_values,
        "best_length": best_lens,
        "peak_index": peak_i,
        "peak_origin": int(origins[peak_i]),
        "peak_t_value": float(arr[peak_i]),
        "peak_length": int(best_lens[peak_i]),
        "share_abs_t_gt_2": significant,
        "l_min": l_min,
        "l_max": l_max,
        "step": step,
        "n_obs": int(n),
    }