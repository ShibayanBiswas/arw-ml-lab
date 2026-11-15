"""Extended column profile — ARCHITECTURE §33.2."""

from __future__ import annotations

import re
from typing import Any

import numpy as np
import pandas as pd

from labcore.data.infer import ColumnProfile, infer_schema

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^\+?[\d\s\-()]{8,}$")
PAN_RE = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")
AADHAAR_RE = re.compile(r"^\d{12}$")
ISIN_RE = re.compile(r"^[A-Z]{2}[A-Z0-9]{9}[0-9]$")
UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I
)
TICKER_RE = re.compile(r"^[A-Z.&-]{1,15}$")

_SAMPLE_CAP = 20_000


def _sample_df(df: pd.DataFrame) -> pd.DataFrame:
    if len(df) <= _SAMPLE_CAP:
        return df
    return df.sample(n=_SAMPLE_CAP, random_state=42)


def _regex_hit_rate(series: pd.Series, pattern: re.Pattern[str]) -> float:
    s = series.dropna().astype(str)
    if s.empty:
        return 0.0
    return float(s.map(lambda v: bool(pattern.match(v.strip()))).mean())


def _monotonic_fraction(series: pd.Series) -> float:
    s = series.dropna()
    if len(s) < 2:
        return 0.0
    if pd.api.types.is_numeric_dtype(s) or pd.api.types.is_datetime64_any_dtype(s):
        vals = s.to_numpy()
        diffs = np.diff(vals)
        return float(np.mean(diffs >= 0))
    return 0.0


def extended_profile(df: pd.DataFrame) -> dict[str, Any]:
    """Build §33.2 profile dict keyed by column name + row-level stats."""
    base = infer_schema(df)
    sample = _sample_df(df)
    columns: dict[str, Any] = {}
    for col in base:
        s = sample[col.name] if col.name in sample.columns else df[col.name]
        non_null = s.dropna()
        entry: dict[str, Any] = {
            "name": col.name,
            "semantic_type": col.semantic_type,
            "physical_dtype": col.physical_dtype,
            "n": int(len(s)),
            "n_missing": int(s.isna().sum()),
            "pct_missing": float(s.isna().mean()) if len(s) else 0.0,
            "n_unique": int(non_null.nunique()),
            "unique_ratio": float(non_null.nunique() / max(len(non_null), 1)),
            "example_values": [_jsonable(v) for v in non_null.head(5).tolist()],
            "monotonic_fraction": _monotonic_fraction(s),
            "name_tokens": _name_tokens(col.name),
            "regex": {
                "email": _regex_hit_rate(s, EMAIL_RE),
                "phone": _regex_hit_rate(s, PHONE_RE),
                "pan": _regex_hit_rate(s, PAN_RE),
                "aadhaar": _regex_hit_rate(s, AADHAAR_RE),
                "isin": _regex_hit_rate(s, ISIN_RE),
                "uuid": _regex_hit_rate(s, UUID_RE),
                "ticker": _regex_hit_rate(s, TICKER_RE),
            },
            "mean_str_len": float(non_null.astype(str).str.len().mean()) if len(non_null) else 0.0,
            "mean_tokens": float(non_null.astype(str).str.split().str.len().mean())
            if len(non_null)
            else 0.0,
        }
        if pd.api.types.is_numeric_dtype(non_null) and len(non_null):
            entry["min"] = float(non_null.min())
            entry["max"] = float(non_null.max())
            entry["mean"] = float(non_null.mean())
            entry["std"] = float(non_null.std(ddof=0)) if len(non_null) > 1 else 0.0
            entry["skew"] = float(non_null.skew()) if len(non_null) > 2 else 0.0
            entry["kurtosis"] = float(non_null.kurtosis()) if len(non_null) > 3 else 0.0
            entry["integer_share"] = float((non_null == non_null.round()).mean())
        columns[col.name] = entry

    # pairwise correlations capped at 200 cols
    num = sample.select_dtypes(include=[np.number])
    if num.shape[1] > 1:
        corr = num.corr(method="spearman").fillna(0.0)
        pairwise = {
            c: {o: float(corr.loc[c, o]) for o in corr.columns if o != c}
            for c in list(corr.columns)[:200]
        }
    else:
        pairwise = {}

    dup_share = float(sample.duplicated().mean()) if len(sample) else 0.0
    return {
        "columns": columns,
        "base_schema": [c.model_dump() for c in base],
        "pairwise_corr": pairwise,
        "duplicate_row_share": dup_share,
        "n_rows": int(len(df)),
        "n_cols": int(df.shape[1]),
        "sampled": len(sample) < len(df),
    }


def _name_tokens(name: str) -> list[str]:
    parts = re.split(r"[_\s\-]+|(?<=[a-z])(?=[A-Z])", name)
    return [p.lower() for p in parts if p]


def _jsonable(v: Any) -> Any:
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, (pd.Timestamp,)):
        return v.isoformat()
    return v


def base_profiles(profile: dict[str, Any]) -> list[ColumnProfile]:
    return [ColumnProfile.model_validate(c) for c in profile["base_schema"]]
