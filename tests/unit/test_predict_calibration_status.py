"""Batch calibration_status labelling — oneshot-c255 (§45.4)."""

from __future__ import annotations

from labcore.predict.calibration_label import calibration_status_label


def test_calibration_status_from_contract() -> None:
    assert calibration_status_label({"calibration_status": "calibrated"}) == "calibrated"
    assert (
        calibration_status_label({"uncertainty": {"calibration_status": "uncalibrated"}})
        == "uncalibrated"
    )


def test_calibration_status_from_pipeline_flag() -> None:
    class _P:
        calibrated_ = True

    assert calibration_status_label({}, _P()) == "calibrated"
    assert calibration_status_label({}, object()) == "uncalibrated"


def test_calibration_status_detects_calibrated_classifier_name() -> None:
    class CalibratedClassifierCV:  # noqa: N801 — mimic sklearn class name
        pass

    assert calibration_status_label({}, CalibratedClassifierCV()) == "calibrated"
