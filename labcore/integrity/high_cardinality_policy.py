"""High-cardinality categorical policy — MI-10 (ARCHITECTURE §46.1, §45.2)."""

from __future__ import annotations

from typing import Any, Literal

import pandas as pd
from sklearn.preprocessing import OneHotEncoder

MI10_RULE = "MI-10"
LAB_DEFAULT_SEED = 42

HIGH_CARDINALITY_LEVELS = 50
ONE_HOT_MAX_LEVELS = 30
IDENTIFIER_MIN_UNIQUE_PCT = 0.50
IDENTIFIER_MIN_DISTINCT = 50

EncoderProposal = Literal["one_hot", "target", "hashing", "count"]

HIGH_CARD_ENCODER_PROPOSALS: tuple[EncoderProposal, ...] = (
    "target",
    "hashing",
    "count",
)


def n_levels(series: pd.Series) -> int:
    return int(series.nunique(dropna=True))


def is_high_cardinality(series: pd.Series) -> bool:
    """True when distinct levels exceed ARCHITECTURE §46.1 MI-10 threshold."""
    return n_levels(series) > HIGH_CARDINALITY_LEVELS


def is_identifier_like_uniqueness(series: pd.Series) -> bool:
    """MI-10: > 50 % unique AND > 50 distinct → identifier-like (exclude by default)."""
    n = len(series)
    if n == 0:
        return False
    nunq = n_levels(series)
    if nunq < IDENTIFIER_MIN_DISTINCT:
        return False
    return (nunq / n) > IDENTIFIER_MIN_UNIQUE_PCT


def propose_categorical_encoders(n_cat_levels: int) -> list[EncoderProposal]:
    """Encoder proposals for a categorical feature by level count."""
    if n_cat_levels > HIGH_CARDINALITY_LEVELS:
        return list(HIGH_CARD_ENCODER_PROPOSALS)
    if n_cat_levels > ONE_HOT_MAX_LEVELS:
        return ["one_hot"]
    return ["one_hot"]


def make_one_hot_encoder(n_cat_levels: int, *, seed: int = LAB_DEFAULT_SEED) -> OneHotEncoder:
    """One-hot capped at 30 levels; rare/infrequent bucket above that (MI-10)."""
    _ = seed
    if n_cat_levels <= ONE_HOT_MAX_LEVELS:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    return OneHotEncoder(
        max_categories=ONE_HOT_MAX_LEVELS,
        handle_unknown="infrequent_if_exist",
        sparse_output=False,
    )


def one_hot_output_within_cap(encoder: OneHotEncoder, series: pd.Series) -> dict[str, Any]:
    """Fit encoder on ``series`` and return output width vs MI-10 cap."""
    values = series.astype(str).fillna("__nan__").to_frame()
    fitted = encoder.fit(values)
    out = fitted.transform(values)
    return {
        "n_levels": n_levels(series),
        "n_output_features": int(out.shape[1]),
        "cap": ONE_HOT_MAX_LEVELS,
        "within_cap": int(out.shape[1]) <= ONE_HOT_MAX_LEVELS + 1,
    }