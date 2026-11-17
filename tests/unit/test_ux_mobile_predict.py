"""UX.MOBILE.PREDICT — ST-UX-04 (oneshot-c182)."""

from __future__ import annotations

from pathlib import Path

from labcore.ux.mobile_predict_contract import (
    ARTEFACT_ID,
    STRESS_ID,
    mobile_predict_manifest,
)

ROOT = Path(__file__).resolve().parents[2]


def test_mobile_predict_manifest_seed_42() -> None:
    m = mobile_predict_manifest(seed=42)
    assert m["id"] == ARTEFACT_ID
    assert m["stress_test"] == STRESS_ID
    assert m["seed"] == 42
    assert m["min_width_px"] == 360
    assert len(m["checks"]) == 2


def test_custom_form_source_markers() -> None:
    src = (
        ROOT / "frontend" / "src" / "components" / "predict" / "CustomPredictForm.tsx"
    ).read_text(encoding="utf-8")
    assert "min-w-[360px]" in src
    assert "predict-form-pane" in src
    assert "predict-result-pane" in src
