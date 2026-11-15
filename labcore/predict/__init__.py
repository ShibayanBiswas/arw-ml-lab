"""Prediction Studio engine (thin Phase 3)."""

from labcore.predict.contract import (
    assert_no_identifier_values,
    build_feature_contract,
    validate_feature_contract,
)
from labcore.predict.score import predict_batch, predict_single

__all__ = [
    "assert_no_identifier_values",
    "build_feature_contract",
    "validate_feature_contract",
    "predict_batch",
    "predict_single",
]
