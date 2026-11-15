"""D4 — Problem family inference — ARCHITECTURE §33.6."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml
from statsmodels.stats.diagnostic import acorr_ljungbox

_WEIGHTS_PATH = Path(__file__).with_name("weights.yaml")


def _load_weights() -> dict[str, Any]:
    with _WEIGHTS_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def _softmax(logits: dict[str, float]) -> dict[str, float]:
    keys = list(logits.keys())
    arr = np.array([logits[k] for k in keys], dtype=float)
    arr = arr - arr.max()
    e = np.exp(arr)
    p = e / e.sum()
    return {k: float(v) for k, v in zip(keys, p, strict=True)}


def infer_family(
    df: pd.DataFrame,
    profile: dict[str, Any],
    d1: dict[str, Any],
    d2: dict[str, Any],
    roles: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    w = _load_weights()
    has_time = 1.0 if d1.get("accepted") else 0.0
    regular = float(d2.get("regularity") or 0.0)
    n_num = sum(
        1
        for c, m in profile["columns"].items()
        if m.get("semantic_type") in {"continuous", "numeric_discrete"}
    )
    n_numeric_series = n_num / max(profile["n_cols"], 1)
    ohlcv = 1.0 if any(r["role"].startswith("price_") for r in roles.values()) else 0.0
    panel = 1.0 if d1.get("entity") else 0.0

    hints = set(w.get("target_name_hints") or [])
    target_named = 0.0
    for name in df.columns:
        tokens = set(re_tokens(name))
        if tokens & hints or name.lower() in hints:
            target_named = 1.0
            break

    autocorr = 0.0
    for name, meta in profile["columns"].items():
        if meta.get("semantic_type") not in {"continuous", "numeric_discrete"}:
            continue
        s = pd.to_numeric(df[name], errors="coerce").dropna()
        if len(s) < 30:
            continue
        try:
            lb = acorr_ljungbox(s, lags=[10], return_df=True)
            p = float(lb["lb_pvalue"].iloc[0])
            if p < 0.01:
                autocorr = 1.0
                break
        except Exception:
            continue

    few_cols_time = 1.0 if has_time and n_num <= 3 else 0.0
    wide_cross_section = 1.0 if (not has_time) and profile["n_cols"] >= 5 else 0.0
    no_target_signal = 1.0 if target_named < 0.5 else 0.0

    evidence = {
        "has_time": has_time,
        "regular": regular,
        "n_numeric_series": n_numeric_series,
        "ohlcv": ohlcv,
        "panel": panel,
        "target_named": target_named,
        "autocorr": autocorr,
        "few_cols_time": few_cols_time,
        "wide_cross_section": wide_cross_section,
        "no_target_signal": no_target_signal,
        "row_order_time": has_time,
    }

    fam_w = w["families"]
    # Forecasting vs sequential: OHLCV / financial panel → sequential; else time_series
    ts_boost = 2.5 if has_time and ohlcv < 1.0 else 0.0
    seq_boost = 2.0 if ohlcv >= 1.0 else 0.0
    # Named forecast targets (Passengers, OT, Temp) still belong to time_series without OHLCV
    seq_target = fam_w["supervised_sequential"]["target_named"] * target_named * (0.2 if has_time and ohlcv < 1.0 else 1.0)
    logits = {
        "time_series": (
            fam_w["time_series"]["has_time"] * has_time
            + fam_w["time_series"]["regular"] * regular
            + fam_w["time_series"]["few_cols_time"] * few_cols_time
            + fam_w["time_series"]["autocorr"] * autocorr
            + fam_w["time_series"]["wide_cross_section"] * wide_cross_section * (0.0 if has_time else 1.0)
            + ts_boost
        ),
        "supervised_sequential": (
            fam_w["supervised_sequential"]["has_time"] * has_time
            + fam_w["supervised_sequential"]["ohlcv"] * ohlcv
            + seq_target
            + fam_w["supervised_sequential"]["autocorr"] * autocorr
            + fam_w["supervised_sequential"]["panel"] * panel
            + fam_w["supervised_sequential"]["few_cols_time"] * few_cols_time
            + seq_boost
        ),
        "supervised_non_sequential": (
            fam_w["supervised_non_sequential"]["target_named"] * target_named
            + fam_w["supervised_non_sequential"]["wide_cross_section"] * wide_cross_section
            + fam_w["supervised_non_sequential"]["has_time"] * has_time
            + fam_w["supervised_non_sequential"].get("intercept", 0.5)
        ),
        "unsupervised": (
            fam_w["unsupervised"]["no_target_signal"] * no_target_signal
            + fam_w["unsupervised"]["wide_cross_section"] * wide_cross_section
            + fam_w["unsupervised"]["target_named"] * target_named
        ),
    }
    scores = _softmax(logits)
    proposed = max(scores, key=scores.get)
    thr = float(w.get("preselect_threshold", 0.55))
    preselected = proposed if scores[proposed] >= thr else None
    financial = bool(ohlcv >= 1.0 or any(r["role"] in {"return", "volume"} for r in roles.values()))

    reasons = [f"evidence:{k}={v}" for k, v in evidence.items() if v]
    return {
        "proposed": preselected or proposed,
        "preselected": preselected is not None,
        "financial": financial,
        "scores": scores,
        "logits": logits,
        "evidence": evidence,
        "reasons": reasons,
        "threshold": thr,
    }


def re_tokens(name: str) -> list[str]:
    import re

    return [t.lower() for t in re.split(r"[_\s\-]+|(?<=[a-z])(?=[A-Z])", name) if t]
