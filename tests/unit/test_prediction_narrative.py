"""Prediction narrative from FACTS — oneshot-c248 (§45.12)."""

from __future__ import annotations

from labcore.predict.narrative import ARTEFACT_ID, prediction_narrative


def test_prediction_narrative_echoes_interval_and_humility() -> None:
    facts = {
        "prediction": 12.5,
        "pred_lower_90": 10.0,
        "pred_upper_90": 15.0,
        "pred_interval_method": "split_conformal_residual",
        "confidence_level": 0.9,
        "humility_action": "warn",
        "ood_score": 4.2,
        "flag_ood": True,
    }
    out = prediction_narrative(facts, seed=42)
    assert out["artefact"] == ARTEFACT_ID
    assert out["mode"] == "numbers-only"
    assert out["seed"] == 42
    assert any("12.5" in f["text"] for f in out["findings"])
    assert any("Interval" in f["text"] for f in out["findings"])
    assert any(f["severity"] == "warn" for f in out["findings"])
    assert "FACTS.prediction" in out["citations"] or "FACTS" in out["citations"]
    # never invent a metric not in FACTS
    blob = out["summary"] + str(out["findings"])
    assert "0.99" not in blob
    assert "fabricat" not in blob.lower()


def test_prediction_narrative_empty_facts() -> None:
    out = prediction_narrative({}, seed=42)
    assert out["findings"]
    assert out["caveats"] == []
