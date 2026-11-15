"""Semantic type inference — ARCHITECTURE §9."""

from __future__ import annotations

import re
import uuid
from typing import Any, Literal

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

SemanticType = Literal[
    "id",
    "datetime",
    "boolean",
    "numeric_discrete",
    "categorical",
    "high_cardinality",
    "text",
    "continuous",
    "constant",
]

BOOL_TOKENS = {
    "0",
    "1",
    "true",
    "false",
    "yes",
    "no",
    "y",
    "n",
    "t",
    "f",
}

ID_NAME_RE = re.compile(r"(^id$|_id$|^code$|uuid|guid|passenger)", re.I)


class ColumnProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    physical_dtype: str
    semantic_type: SemanticType
    n_unique: int
    pct_unique: float
    pct_missing: float
    example_values: list[Any] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    role_suggestion: str | None = None  # feature | target | id | time | exclude


def _is_uuid_like(series: pd.Series) -> bool:
    sample = series.dropna().astype(str).head(50)
    if sample.empty:
        return False
    ok = 0
    for v in sample:
        try:
            uuid.UUID(str(v))
            ok += 1
        except Exception:
            pass
    return ok / max(len(sample), 1) >= 0.9


def _datetime_parse_rate(series: pd.Series) -> float:
    s = series.dropna()
    if s.empty:
        return 0.0
    if pd.api.types.is_datetime64_any_dtype(s):
        return 1.0
    parsed = pd.to_datetime(s.astype(str), errors="coerce", utc=False)
    return float(parsed.notna().mean())


def _bool_like(series: pd.Series) -> bool:
    s = series.dropna()
    if s.empty:
        return False
    if pd.api.types.is_bool_dtype(s):
        return True
    vals = {str(v).strip().lower() for v in s.unique()}
    return vals.issubset(BOOL_TOKENS) and len(vals) <= 2


def infer_column(name: str, series: pd.Series) -> ColumnProfile:
    n = len(series)
    n_miss = int(series.isna().sum())
    pct_missing = float(n_miss / n) if n else 0.0
    non_null = series.dropna()
    n_unique = int(non_null.nunique())
    pct_unique = float(n_unique / max(len(non_null), 1))
    examples = [_jsonable(v) for v in non_null.head(3).tolist()]
    warnings: list[str] = []
    physical = str(series.dtype)

    if n_unique <= 1 and len(non_null) > 0:
        return ColumnProfile(
            name=name,
            physical_dtype=physical,
            semantic_type="constant",
            n_unique=n_unique,
            pct_unique=pct_unique,
            pct_missing=pct_missing,
            example_values=examples,
            warnings=["constant_or_quasi_constant"],
            role_suggestion="exclude",
        )

    # ID
    if ID_NAME_RE.search(name) or (
        pct_unique >= 0.98 and (pd.api.types.is_integer_dtype(non_null) or _is_uuid_like(non_null))
    ):
        return ColumnProfile(
            name=name,
            physical_dtype=physical,
            semantic_type="id",
            n_unique=n_unique,
            pct_unique=pct_unique,
            pct_missing=pct_missing,
            example_values=examples,
            role_suggestion="id",
        )

    dt_rate = _datetime_parse_rate(series)
    if dt_rate >= 0.95:
        return ColumnProfile(
            name=name,
            physical_dtype=physical,
            semantic_type="datetime",
            n_unique=n_unique,
            pct_unique=pct_unique,
            pct_missing=pct_missing,
            example_values=examples,
            role_suggestion="time",
        )

    if _bool_like(series):
        return ColumnProfile(
            name=name,
            physical_dtype=physical,
            semantic_type="boolean",
            n_unique=n_unique,
            pct_unique=pct_unique,
            pct_missing=pct_missing,
            example_values=examples,
            role_suggestion="feature",
        )

    if pd.api.types.is_numeric_dtype(non_null):
        int_like = pd.api.types.is_integer_dtype(non_null) or (
            pd.api.types.is_float_dtype(non_null) and bool((non_null == non_null.round()).all())
        )
        if int_like and n_unique <= min(20, max(1, int(0.05 * n))):
            return ColumnProfile(
                name=name,
                physical_dtype=physical,
                semantic_type="numeric_discrete",
                n_unique=n_unique,
                pct_unique=pct_unique,
                pct_missing=pct_missing,
                example_values=examples,
                warnings=["could_be_categorical"],
                role_suggestion="feature",
            )
        return ColumnProfile(
            name=name,
            physical_dtype=physical,
            semantic_type="continuous",
            n_unique=n_unique,
            pct_unique=pct_unique,
            pct_missing=pct_missing,
            example_values=examples,
            role_suggestion="feature",
        )

    # Object / string — free text (names, comments): long/spaced OR near-unique with spaces
    as_str = non_null.astype(str)
    mean_len = float(as_str.str.len().mean()) if len(as_str) else 0.0
    space_frac = float(as_str.str.contains(r"\s").mean()) if len(as_str) else 0.0
    text_like = (mean_len > 25 and space_frac > 0.3) or (
        pct_unique > 0.85 and space_frac > 0.5 and mean_len > 12
    )
    if text_like:
        return ColumnProfile(
            name=name,
            physical_dtype=physical,
            semantic_type="text",
            n_unique=n_unique,
            pct_unique=pct_unique,
            pct_missing=pct_missing,
            example_values=examples,
            warnings=["text_like_excluded"],
            role_suggestion="exclude",
        )

    if n_unique <= 50 or pct_unique <= 0.05:
        return ColumnProfile(
            name=name,
            physical_dtype=physical,
            semantic_type="categorical",
            n_unique=n_unique,
            pct_unique=pct_unique,
            pct_missing=pct_missing,
            example_values=examples,
            role_suggestion="feature",
        )

    warnings.append("high_cardinality")
    return ColumnProfile(
        name=name,
        physical_dtype=physical,
        semantic_type="high_cardinality",
        n_unique=n_unique,
        pct_unique=pct_unique,
        pct_missing=pct_missing,
        example_values=examples,
        warnings=warnings,
        role_suggestion="feature",
    )


def infer_schema(df: pd.DataFrame) -> list[ColumnProfile]:
    return [infer_column(str(c), df[c]) for c in df.columns]


def _jsonable(v: Any) -> Any:
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, (np.bool_,)):
        return bool(v)
    if pd.isna(v):
        return None
    return v
