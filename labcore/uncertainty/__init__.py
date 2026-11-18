"""Uncertainty / calibration / conformal (Phase 3 thin)."""

from labcore.uncertainty.calibration import calibrate_binary, expected_calibration_error
from labcore.uncertainty.conformal import split_conformal_aps, split_conformal_regression
from labcore.uncertainty.conformal_dl import (
    conformal_qhat_from_residuals,
    predict_with_conformal_residual,
)
from labcore.uncertainty.deep_ensemble import deep_ensemble_predict
from labcore.uncertainty.mc_dropout import mc_dropout_predict

__all__ = [
    "calibrate_binary",
    "expected_calibration_error",
    "split_conformal_aps",
    "split_conformal_regression",
    "mc_dropout_predict",
    "deep_ensemble_predict",
    "conformal_qhat_from_residuals",
    "predict_with_conformal_residual",
]
