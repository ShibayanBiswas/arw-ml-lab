"""Fractional differentiation (López de Prado, AFML ch. 5) — thin causal FFD."""

from __future__ import annotations

from typing import Any

import numpy as np


def get_weights_ffd(d: float, *, thresh: float = 1e-5) -> np.ndarray:
    """Binomial FFD weights; stop when |w_k| < thresh."""
    if d < 0 or d > 1:
        raise ValueError("d must be in [0, 1]")
    w = [1.0]
    k = 1
    while k < 10_000:
        w_k = -w[-1] * (d - k + 1) / k
        if abs(w_k) < thresh:
            break
        w.append(w_k)
        k += 1
    return np.asarray(w, dtype=float)


def frac_diff_ffd(series: np.ndarray, d: float, *, thresh: float = 1e-5) -> np.ndarray:
    """Apply fixed-width fractional diff; past-only weights (no look-ahead)."""
    s = np.asarray(series, dtype=float).ravel()
    w = get_weights_ffd(d, thresh=thresh)
    width = len(w) - 1
    out = np.full(len(s), np.nan, dtype=float)
    w_rev = w[::-1]
    for i in range(width, len(s)):
        out[i] = float(np.dot(w_rev, s[i - width : i + 1]))
    return out


def scan_min_ffd(
    series: np.ndarray,
    *,
    d_min: float = 0.0,
    d_max: float = 1.0,
    d_step: float = 0.05,
    adf_alpha: float = 0.05,
    thresh: float = 1e-5,
    maxlag: int = 10,
) -> dict[str, Any]:
    """Scan d grid: ADF on frac-diff vs log-price, corr with original; pick min stationary d."""
    from statsmodels.tsa.stattools import adfuller

    s = np.asarray(series, dtype=float).ravel()
    s = s[np.isfinite(s)]
    if len(s) < 50:
        raise ValueError("need ≥50 finite observations for min-FFD scan")
    base = s
    grid: list[float] = []
    d = d_min
    while d <= d_max + 1e-12:
        grid.append(round(d, 10))
        d += d_step

    rows: list[dict[str, Any]] = []
    d_star: float | None = None
    for dv in grid:
        fd = frac_diff_ffd(base, dv, thresh=thresh)
        valid = np.isfinite(fd)
        fd_valid = fd[valid]
        base_valid = base[valid]
        if len(fd_valid) < maxlag + 5:
            rows.append(
                {
                    "d": dv,
                    "adf_statistic": None,
                    "adf_pvalue": None,
                    "corr_with_original": None,
                }
            )
            continue
        adf = adfuller(fd_valid, maxlag=maxlag, autolag="AIC", result_object=True)
        corr = float(np.corrcoef(base_valid, fd_valid)[0, 1])
        pval = float(adf.pvalue)
        stat = float(adf.statistic)
        rows.append(
            {
                "d": dv,
                "adf_statistic": stat,
                "adf_pvalue": pval,
                "corr_with_original": corr,
            }
        )
        if d_star is None and dv > 0 and pval < adf_alpha:
            d_star = dv

    return {
        "d_grid": grid,
        "rows": rows,
        "d_star": d_star,
        "adf_alpha": adf_alpha,
        "thresh": thresh,
    }