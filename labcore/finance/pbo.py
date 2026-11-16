"""Probability of Backtest Overfitting — CSCV (Bailey et al. 2017).

Thin implementation of the CSCV estimator used when TradingLab has no PBO
module (ARCHITECTURE §13.2). Matrix T×M of per-period OOS performance;
S even blocks; for each combination of S/2 IS blocks pick the best config
and score its OOS relative rank.
"""

from __future__ import annotations

from itertools import combinations
from math import comb
from typing import Any

import numpy as np


def probability_of_backtest_overfitting(
    performance: np.ndarray,
    *,
    n_blocks: int = 16,
    seed: int = 42,
) -> dict[str, Any]:
    """Compute PBO from a T×M performance matrix (rows=periods, cols=configs).

    Returns PBO, logit histogram bin edges/counts, and mean relative rank.
    Never fabricates: if matrix too small, status=not computed.
    """
    _ = seed
    mat = np.asarray(performance, dtype=float)
    if mat.ndim != 2:
        raise ValueError("performance must be 2-d T×M")
    t, m = mat.shape
    if n_blocks % 2 != 0 or n_blocks < 2:
        raise ValueError("n_blocks must be even and ≥ 2")
    if t < n_blocks or m < 2:
        return {
            "pbo": float("nan"),
            "status": "not computed",
            "reason": f"need T≥{n_blocks} and M≥2 (got T={t}, M={m})",
            "n_combinations": 0,
        }

    # Split rows into S contiguous blocks
    blocks = np.array_split(np.arange(t), n_blocks)
    half = n_blocks // 2
    logits: list[float] = []
    n_neg = 0
    n_comb = int(comb(n_blocks, half))

    for is_ids in combinations(range(n_blocks), half):
        oos_ids = [i for i in range(n_blocks) if i not in is_ids]
        is_idx = np.concatenate([blocks[i] for i in is_ids])
        oos_idx = np.concatenate([blocks[i] for i in oos_ids])
        is_perf = mat[is_idx].mean(axis=0)
        best = int(np.argmax(is_perf))
        oos_perf = mat[oos_idx].mean(axis=0)
        # relative rank ω̄ of the IS-best config among OOS (higher better)
        ranks = oos_perf.argsort().argsort().astype(float)  # 0..M-1
        omega = (ranks[best] + 1.0) / m  # in (0,1]
        # avoid 0/1 for logit
        omega = float(np.clip(omega, 1e-6, 1 - 1e-6))
        lam = float(np.log(omega / (1.0 - omega)))
        logits.append(lam)
        if lam <= 0:
            n_neg += 1

    pbo = n_neg / max(len(logits), 1)
    hist_counts, hist_edges = np.histogram(logits, bins=20)
    return {
        "pbo": float(pbo),
        "status": "ok",
        "n_combinations": n_comb,
        "n_logits": len(logits),
        "mean_logit": float(np.mean(logits)),
        "logit_hist_counts": hist_counts.astype(int).tolist(),
        "logit_hist_edges": hist_edges.astype(float).tolist(),
        "n_blocks": n_blocks,
        "n_configs": m,
        "n_periods": t,
    }
