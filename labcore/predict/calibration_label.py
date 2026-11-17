"""Label prediction probabilities as calibrated / uncalibrated (§45.4)."""

from __future__ import annotations

from typing import Any


def _pipeline_looks_calibrated(pipeline: Any) -> bool:
    if pipeline is None:
        return False
    if bool(getattr(pipeline, "calibrated_", False)):
        return True
    name = type(pipeline).__name__
    if "CalibratedClassifier" in name:
        return True
    # sklearn Pipeline / FeatureUnion style
    steps = getattr(pipeline, "named_steps", None) or getattr(pipeline, "steps", None)
    if isinstance(steps, dict):
        iters = steps.values()
    elif isinstance(steps, (list, tuple)):
        iters = (s[-1] if isinstance(s, (list, tuple)) else s for s in steps)
    else:
        iters = ()
    for step in iters:
        if step is None:
            continue
        if "CalibratedClassifier" in type(step).__name__:
            return True
        if bool(getattr(step, "calibrated_", False)):
            return True
    return False


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
    if _pipeline_looks_calibrated(pipeline):
        return "calibrated"
    return "uncalibrated"
