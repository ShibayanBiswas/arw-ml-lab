"""D8 — Distribution drift — ARCHITECTURE §33.11."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy import stats


def _psi(expected: np.ndarray, actual: np.ndarray, bins: int = 10) -> float:
    qs = np.linspace(0, 100, bins + 1)
    breaks = np.unique(np.percentile(expected, qs))
    if len(breaks) < 3:
        return 0.0
    e_counts = np.histogram(expected, bins=breaks)[0].astype(float)
    a_counts = np.histogram(actual, bins=breaks)[0].astype(float)
    e_counts = (e_counts + 1e-6) / (e_counts.sum() + 1e-6 * len(e_counts))
    a_counts = (a_counts + 1e-6) / (a_counts.sum() + 1e-6 * len(a_counts))
    return float(np.sum((a_counts - e_counts) * np.log(a_counts / e_counts)))


def drift_report(parent_df: pd.DataFrame, child_df: pd.DataFrame) -> dict[str, Any]:
    drift: dict[str, Any] = {}
    for c in sorted(set(parent_df.columns) & set(child_df.columns)):
        a = parent_df[c]
        b = child_df[c]
        entry: dict[str, Any] = {}
        if pd.api.types.is_numeric_dtype(a) and pd.api.types.is_numeric_dtype(b):
            aa = pd.to_numeric(a, errors="coerce").dropna().to_numpy()
            bb = pd.to_numeric(b, errors="coerce").dropna().to_numpy()
            if len(aa) > 20 and len(bb) > 20:
                entry["psi"] = _psi(aa, bb)
                try:
                    _, p = stats.ks_2samp(aa, bb)
                    entry["ks_pvalue"] = float(p)
                except Exception:
                    entry["ks_pvalue"] = None
                flag = (
                    "red" if entry["psi"] > 0.25 else ("amber" if entry["psi"] > 0.1 else "green")
                )
                entry["flag"] = flag
        else:
            # chi-square on top categories
            ca = a.astype(str).value_counts()
            cb = b.astype(str).value_counts()
            idx = sorted(set(ca.index) | set(cb.index))[:50]
            if len(idx) >= 2:
                obs = np.array([[ca.get(i, 0), cb.get(i, 0)] for i in idx], dtype=float)
                try:
                    chi2, p, _, _ = stats.chi2_contingency(obs + 1e-6)
                    entry["chi2"] = float(chi2)
                    entry["chi2_pvalue"] = float(p)
                except Exception:
                    pass
        if entry:
            drift[c] = entry
    return {"columns": drift}
