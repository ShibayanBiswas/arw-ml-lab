"""Feature-contract schema accepts pred_threshold / calibration / uncertainty (oneshot-c280)."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
from labcore.predict.contract import validate_feature_contract

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads(
    (ROOT / "docs" / "contracts" / "feature_contract.schema.json").read_text(encoding="utf-8")
)


def _minimal_contract(**extra: object) -> dict:
    base = {
        "contract_version": "1.0",
        "dataset_id": "DS1",
        "task": "binary",
        "seed": 42,
        "features": [{"name": "age", "kind": "numeric"}],
    }
    base.update(extra)
    return base


def test_schema_lists_uq_fields() -> None:
    props = SCHEMA["properties"]
    assert "pred_threshold" in props
    assert "calibration_status" in props
    assert "uncertainty" in props


def test_validate_accepts_train_uq_fields() -> None:
    contract = _minimal_contract(
        pred_threshold=0.42,
        calibration_status="uncalibrated",
        uncertainty={
            "method": "split_conformal_residual",
            "confidence_level": 0.9,
            "conformal_qhat": 1.23,
            "source": "oof",
        },
    )
    jsonschema.validate(contract, SCHEMA)
    assert validate_feature_contract(contract) == []


def test_validate_rejects_bad_calibration_status() -> None:
    contract = _minimal_contract(calibration_status="not-a-real-status")
    errs = validate_feature_contract(contract)
    assert errs, "expected schema errors for invalid calibration_status"
