"""D5 — Target and feature recommendation — ARCHITECTURE §33.7."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml
from sklearn.feature_selection import mutual_info_classif, mutual_info_regression

from labcore.intake.horizon import horizon_guard

_WEIGHTS_PATH = Path(__file__).with_name("weights.yaml")


def _name_hint(name: str, hints: set[str]) -> float:
    low = name.lower()
    if low in hints:
        return 1.0
    tokens = set(low.replace("-", "_").split("_"))
    return 1.0 if tokens & hints else 0.0


def recommend_targets_features(
    df: pd.DataFrame,
    profile: dict[str, Any],
    roles: dict[str, dict[str, Any]],
    family: dict[str, Any],
    d2: dict[str, Any],
) -> dict[str, Any]:
    with _WEIGHTS_PATH.open(encoding="utf-8") as f:
        hints = set(yaml.safe_load(f).get("target_name_hints") or [])

    financial = bool(family.get("financial"))
    fam = family.get("proposed")
    cols = list(df.columns)
    last = cols[-1] if cols else None
    mi_rank: dict[str, int] = {}

    candidates: list[dict[str, Any]] = []
    if financial or fam == "supervised_sequential":
        # Never propose raw price as target
        candidates = [
            {
                "column": "__derived__",
                "derived": {
                    "builder": "triple_barrier",
                    "params": {"pt": "2x_daily_vol", "sl": "2x_daily_vol", "vertical": 10},
                },
                "confidence": 0.85,
                "reasons": ["financial_no_raw_price", "triple_barrier_default"],
            },
            {
                "column": "__derived__",
                "derived": {"builder": "fwd_log_return", "params": {"h": 1}},
                "confidence": 0.7,
                "reasons": ["forward_log_return"],
            },
            {
                "column": "__derived__",
                "derived": {"builder": "direction", "params": {"h": 1}},
                "confidence": 0.65,
                "reasons": ["direction_sign"],
            },
            {
                "column": "__derived__",
                "derived": {"builder": "trend_scanning", "params": {}},
                "confidence": 0.6,
                "reasons": ["trend_scanning"],
            },
            {
                "column": "__derived__",
                "derived": {"builder": "realised_vol", "params": {"window": 21}},
                "confidence": 0.55,
                "reasons": ["realised_volatility"],
            },
        ]
    else:
        for name in cols:
            r = roles.get(name, {})
            if r.get("hard_exclude") or r.get("role") in {
                "time_index",
                "entity_id",
                "row_id",
                "pii",
                "text",
                "constant",
                "volume",
            }:
                continue
            if str(r.get("role", "")).startswith("price_"):
                continue
            if str(r.get("role", "")).startswith("duplicate_of"):
                continue
            meta = profile["columns"].get(name, {})
            type_ok = meta.get("semantic_type") in {
                "continuous",
                "numeric_discrete",
                "boolean",
                "categorical",
            }
            score = (
                0.35 * _name_hint(name, hints)
                + 0.15 * (1.0 if name == last else 0.0)
                + 0.15 * (1.0 if type_ok else 0.0)
                + 0.10 * (1.0 - float(meta.get("pct_missing", 0)))
                + 0.10 * (0.0 if r.get("role") == "row_id" else 1.0)
            )
            # light predictability via MI later
            candidates.append(
                {
                    "column": name,
                    "derived": None,
                    "confidence": float(min(1.0, score + 0.15)),
                    "target_score": score,
                    "reasons": [f"target_score={score:.2f}"],
                }
            )
        candidates.sort(key=lambda x: x.get("target_score", 0), reverse=True)

    # Task type from top non-derived target
    task: dict[str, Any] | None = None
    primary = next((c for c in candidates if c.get("column") != "__derived__"), None)
    if fam == "time_series":
        # prefer last numeric / Passengers / OT
        for pref in ("OT", "Passengers", "passengers", "Temp", "temp"):
            if pref in df.columns:
                primary = {
                    "column": pref,
                    "derived": None,
                    "confidence": 0.9,
                    "reasons": ["ts_target_name"],
                }
                candidates = [primary] + [c for c in candidates if c.get("column") != pref]
                break
        if primary is None and candidates:
            primary = candidates[0]
        task = {
            "type": "forecast_univariate" if profile["n_cols"] <= 3 else "forecast_multivariate",
            "confidence": 0.8,
            "alternatives": [],
            "reasons": ["time_series_family"],
        }
    elif fam == "unsupervised":
        candidates = []
        task = {"type": "unsupervised", "confidence": 0.8, "reasons": ["no_strong_target"]}
        primary = None
    elif primary:
        y = df[primary["column"]]
        nunq = int(y.nunique(dropna=True))
        if nunq == 2:
            ttype = "binary"
        elif pd.api.types.is_numeric_dtype(y) and nunq > 20:
            ttype = "regression"
        elif nunq <= 20:
            ttype = "multiclass"
        else:
            ttype = "regression"
        task = {"type": ttype, "confidence": 0.75, "alternatives": [], "reasons": [f"n_unique={nunq}"]}

        # MI ranks for features
        sample = df.sample(n=min(len(df), 20_000), random_state=42) if len(df) > 20_000 else df
        feat_cols = [
            c
            for c, r in roles.items()
            if r.get("included")
            and c != primary["column"]
            and not r.get("hard_exclude")
            and not str(r.get("role", "")).startswith("price_")
        ]
        try:
            X = sample[feat_cols].select_dtypes(include=[np.number]).fillna(0)
            if not X.empty and primary["column"] in sample.columns:
                yy = sample[primary["column"]]
                if ttype in {"binary", "multiclass"}:
                    yv = pd.Categorical(yy).codes
                    mi = mutual_info_classif(X, yv, random_state=42)
                else:
                    yv = pd.to_numeric(yy, errors="coerce").fillna(0)
                    mi = mutual_info_regression(X, yv, random_state=42)
                order = list(np.argsort(-mi))
                for rank, idx in enumerate(order, start=1):
                    mi_rank[X.columns[idx]] = rank
                # boost target score with predictability
                if len(mi):
                    primary["confidence"] = float(min(1.0, primary["confidence"] + 0.1))
        except Exception:
            mi_rank = {}

    features: list[dict[str, Any]] = []
    for name, r in roles.items():
        if not r.get("included") or r.get("hard_exclude"):
            continue
        if primary and name == primary.get("column"):
            continue
        meta = profile["columns"].get(name, {})
        encoder = None
        transform = None
        imputer = "median" if meta.get("semantic_type") in {"continuous", "numeric_discrete"} else "most_frequent"
        if r["role"] == "feature_categorical":
            nuniq = meta.get("n_unique", 0)
            encoder = "target" if nuniq and nuniq > 20 else "one_hot"
        if meta.get("skew", 0) and abs(float(meta["skew"])) > 1:
            transform = "yeo_johnson"
        if r["role"] == "volume":
            transform = "log1p"
        features.append(
            {
                "column": name,
                "role": r["role"],
                "encoder": encoder,
                "transform": transform,
                "imputer": imputer,
                "rank": mi_rank.get(name),
                "confidence": r.get("confidence", 0.6),
            }
        )

    m = (d2.get("seasonal_periods") or [None])[0]
    hz = horizon_guard(profile["n_rows"], d2.get("alias"), m=m)
    return {
        "targets": candidates[:8],
        "features": features,
        "task": task,
        "horizon": hz if fam in {"time_series", "supervised_sequential"} else None,
    }
