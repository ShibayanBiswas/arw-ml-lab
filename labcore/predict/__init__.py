"""Prediction Studio engine (Phase 3 / 3A thin)."""

from labcore.predict.contract import (
    assert_no_identifier_values,
    build_feature_contract,
    validate_feature_contract,
)
from labcore.predict.score import predict_batch, predict_single
from labcore.predict.template import (
    predictions_to_safe_csv,
    sample_row_from_contract,
    template_csv_bytes,
    template_dataframe,
    template_xlsx_bytes,
)
from labcore.predict.validate import ValidationReport, validate_predict_frame

__all__ = [
    "assert_no_identifier_values",
    "build_feature_contract",
    "validate_feature_contract",
    "predict_batch",
    "predict_single",
    "validate_predict_frame",
    "ValidationReport",
    "sample_row_from_contract",
    "template_dataframe",
    "template_csv_bytes",
    "template_xlsx_bytes",
    "predictions_to_safe_csv",
]
