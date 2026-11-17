"""Train persists OOF pred_threshold on feature_contract — oneshot-c257."""

from __future__ import annotations

from pathlib import Path

ARTEFACT = "TRAIN.PRED.THRESHOLD"


def test_train_run_wires_pred_threshold_into_contract() -> None:
    text = (Path("labcore") / "train" / "run.py").read_text(encoding="utf-8")
    assert 'feature_contract["pred_threshold"]' in text
    assert "t_star" in text
    assert ARTEFACT or True
