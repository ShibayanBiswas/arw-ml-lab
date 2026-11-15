"""D3 — Column role inference — ARCHITECTURE §33.5."""

from __future__ import annotations

import re
from typing import Any

import numpy as np
import pandas as pd

OHLC_MAP = {
    "open": "price_open",
    "high": "price_high",
    "low": "price_low",
    "close": "price_close",
    "adj close": "price_adj_close",
    "adj_close": "price_adj_close",
    "ltp": "price_close",
    "nav": "price_close",
}


def _ohlcv_consistency(df: pd.DataFrame, mapping: dict[str, str]) -> bool:
    o, h, low, c = mapping.get("open"), mapping.get("high"), mapping.get("low"), mapping.get("close")
    if not all([o, h, low, c]):
        return False
    hi = df[h].astype(float)
    lo = df[low].astype(float)
    op = df[o].astype(float)
    cl = df[c].astype(float)
    ok = ((hi >= np.maximum(op, cl)) & (lo <= np.minimum(op, cl))).mean()
    return float(ok) >= 0.99


def detect_roles(
    df: pd.DataFrame,
    profile: dict[str, Any],
    d1: dict[str, Any],
    d2: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    roles: dict[str, dict[str, Any]] = {}
    cols = profile["columns"]

    # OHLCV by name
    lower = {c.lower().strip(): c for c in df.columns}
    ohlcv_cols: dict[str, str] = {}
    for key, _role in OHLC_MAP.items():
        if key in lower:
            ohlcv_cols[key if key != "adj close" else "adj_close"] = lower[key]
    if "volume" in lower or "vol" in lower or "qty" in lower or "turnover" in lower:
        for k in ("volume", "vol", "qty", "turnover"):
            if k in lower:
                ohlcv_cols["volume"] = lower[k]
                break
    for k in ("date", "datetime", "timestamp", "time"):
        if k in lower:
            ohlcv_cols["time"] = lower[k]
            break

    ohlcv_ok = False
    if {"open", "high", "low", "close"}.issubset(ohlcv_cols):
        ohlcv_ok = _ohlcv_consistency(
            df,
            {
                "open": ohlcv_cols["open"],
                "high": ohlcv_cols["high"],
                "low": ohlcv_cols["low"],
                "close": ohlcv_cols["close"],
            },
        )

    time_col = (d1.get("accepted") or {}).get("column")
    entity_col = (d1.get("entity") or {}).get("column")
    composite = (d1.get("accepted") or {}).get("composite_of") or []

    seen_values: dict[str, str] = {}  # hash -> first col for duplicates

    for name in df.columns:
        meta = cols.get(name, {})
        tags: list[str] = []
        reasons: list[str] = []
        role = "feature_numeric"
        conf = 0.6
        included = True

        if name == time_col or name in composite:
            role, conf, included = "time_index", 0.95, False
            reasons.append("d1_time_index")
        elif name == entity_col:
            role, conf, included = "entity_id", 0.9, False
            reasons.append("d1_panel_entity")
        elif name in ohlcv_cols.values() and ohlcv_ok:
            for k, v in ohlcv_cols.items():
                if v == name:
                    if k == "volume":
                        role = "volume"
                    elif k == "time":
                        role = "time_index"
                        included = False
                    else:
                        role = OHLC_MAP.get(k.replace("_", " "), OHLC_MAP.get(k, "price_close"))
                    conf = 0.95
                    reasons.append("ohlcv_block")
                    break
        elif meta.get("semantic_type") == "constant" or meta.get("n_unique") == 1:
            role, conf, included = "constant", 1.0, False
            reasons.append("n_unique_1")
        elif meta.get("pct_missing", 0) >= 0.60:
            tags.append("high_missing")
            included = False
            role = "feature_categorical" if meta.get("semantic_type") in {
                "categorical",
                "high_cardinality",
                "text",
            } else "feature_numeric"
            reasons.append("missing_ge_60pct")
        elif meta.get("semantic_type") == "id" or (
            meta.get("unique_ratio", 0) >= 0.98
            and (
                re.search(r"(^id$|_id$|Id$|index|unnamed)", name, re.I)
                or meta.get("regex", {}).get("uuid", 0) >= 0.5
                or (
                    pd.api.types.is_integer_dtype(df[name])
                    and float((df[name].dropna().diff().dropna() == 1).mean()) > 0.95
                )
            )
        ):
            role, conf, included = "row_id", 0.95, False
            reasons.append("row_id_rule")
        elif meta.get("regex", {}).get("email", 0) >= 0.5 or meta.get("regex", {}).get("pan", 0) >= 0.5:
            role, conf, included = "pii", 0.95, False
            reasons.append("pii_regex")
        elif (
            meta.get("semantic_type") == "text"
            or re.search(r"(^name$|email|mobile|address|phone)", name, re.I)
            or (meta.get("mean_str_len", 0) > 15 and "name" in name.lower())
            or (meta.get("mean_str_len", 0) > 30 and meta.get("mean_tokens", 0) > 5)
        ):
            # Person names / free text → PII or text exclude (NLP out of scope)
            if re.search(r"(^name$|email|mobile|address|phone)", name, re.I) or "name" in name.lower():
                role, conf, included = "pii", 0.9, False
                reasons.append("pii_or_text")
            else:
                role, conf, included = "text", 0.9, False
                reasons.append("text_out_of_scope")
        elif re.search(r"^(weight|w|sample_weight|exposure)$", name, re.I):
            role, conf = "weight", 0.8
        elif re.search(r"(ret|return|pct_change)", name, re.I):
            role, conf = "return", 0.75
        elif meta.get("semantic_type") == "boolean":
            role = "feature_boolean"
        elif meta.get("semantic_type") in {"categorical", "high_cardinality"}:
            role = "feature_categorical"
            if meta.get("semantic_type") == "high_cardinality":
                tags.append("high_cardinality")
        elif meta.get("semantic_type") == "datetime":
            role = "datetime_feature"
        else:
            role = "feature_numeric"

        # duplicate detection
        try:
            key = pd.util.hash_pandas_object(df[name], index=False).sum()
            key_s = str(key)
            if key_s in seen_values:
                role = f"duplicate_of:{seen_values[key_s]}"
                included = False
                conf = 1.0
                reasons.append("identical_values")
            else:
                seen_values[key_s] = name
        except Exception:
            pass

        roles[name] = {
            "role": role,
            "confidence": conf,
            "tags": tags,
            "reasons": reasons,
            "included": included,
            "hard_exclude": role.split(":")[0]
            in {
                "row_id",
                "constant",
                "near_constant",
                "duplicate_of",
                "text",
                "pii",
                "time_index",
                "entity_id",
            }
            or role.startswith("duplicate_of"),
        }

    return roles
