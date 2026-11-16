"""Feature drift via scipy Kolmogorov–Smirnov (library-backed)."""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy.stats import ks_2samp


def ks_drift_report(
    reference: np.ndarray,
    current: np.ndarray,
    *,
    feature_names: list[str] | None = None,
    alpha: float = 0.01,
) -> dict[str, Any]:
    """Per-column two-sample KS test; flag when p < alpha."""
    ref = np.asarray(reference, dtype=float)
    cur = np.asarray(current, dtype=float)
    if ref.ndim == 1:
        ref = ref.reshape(-1, 1)
        cur = cur.reshape(-1, 1)
    if ref.shape[1] != cur.shape[1]:
        raise ValueError("reference and current must share n_features")
    n_feat = ref.shape[1]
    names = feature_names or [f"f{i}" for i in range(n_feat)]
    rows: list[dict[str, Any]] = []
    for j in range(n_feat):
        a = ref[:, j]
        b = cur[:, j]
        a = a[np.isfinite(a)]
        b = b[np.isfinite(b)]
        if len(a) < 5 or len(b) < 5:
            rows.append(
                {
                    "feature": names[j],
                    "statistic": float("nan"),
                    "pvalue": float("nan"),
                    "drift": False,
                    "status": "not computed",
                }
            )
            continue
        stat, pval = ks_2samp(a, b)
        rows.append(
            {
                "feature": names[j],
                "statistic": float(stat),
                "pvalue": float(pval),
                "drift": bool(pval < alpha),
                "status": "ok",
            }
        )
    return {
        "id": "MON.T.KS_DRIFT",
        "alpha": alpha,
        "n_features": n_feat,
        "n_drifted": int(sum(1 for r in rows if r["drift"])),
        "features": rows,
        "seed": 42,
    }
