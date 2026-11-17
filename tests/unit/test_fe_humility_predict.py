"""CustomPredictForm surfaces PRED.HUMILITY (oneshot-c193)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORM = ROOT / "frontend" / "src" / "components" / "predict" / "CustomPredictForm.tsx"


def test_custom_form_shows_humility() -> None:
    src = FORM.read_text(encoding="utf-8")
    assert 'data-artefact="PRED.HUMILITY"' in src
    assert "abstained" in src
    assert "needs_human_review" in src
