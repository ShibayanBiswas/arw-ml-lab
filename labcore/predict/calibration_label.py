"""Label prediction probabilities as calibrated / uncalibrated (§45.4)."""

from __future__ import annotations

from typing import Any


def calibration_status_label(
    feature_contract: dict[str, Any] | None,
    pipeline: Any = None,
) -> str:
    """Return ``calibrated`` or ``uncalibrated`` from contract / pipeline flags."""
    contract = feature_contract or {}
    status = contract.get("calibration_status")
    if status in ("calibrated", "uncalibrated"):
        return str(status)
    unc = contract.get("uncertainty") or {}
    if isinstance(unc, dict) and unc.get("calibration_status") in ("calibrated", "uncalibrated"):
        return str(unc["calibration_status"])
    if pipeline is not None and bool(getattr(pipeline, "calibrated_", False)):
        return "calibrated"
    return "uncalibrated"
