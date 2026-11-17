"""Offline artefact UX.MOBILE.PREDICT — ST-UX-04 (§45.11 / §46.4)."""

from __future__ import annotations

from pathlib import Path

ARTEFACT_ID = "UX.MOBILE.PREDICT"
STRESS_ID = "ST-UX-04"

ROOT = Path(__file__).resolve().parents[2]
CUSTOM_FORM = ROOT / "frontend" / "src" / "components" / "predict" / "CustomPredictForm.tsx"
TRAIN_WB = ROOT / "frontend" / "src" / "components" / "train" / "TrainWorkbench.tsx"


class MobilePredictContractError(ValueError):
    """Raised when ST-UX-04 markers are missing from FE sources."""


def assert_custom_form_stacks() -> dict[str, object]:
    src = CUSTOM_FORM.read_text(encoding="utf-8")
    required = (
        "min-w-[360px]",
        "flex flex-col",
        "predict-form-pane",
        "predict-result-pane",
        "ST-UX-04",
        "lg:grid-cols-2",
    )
    missing = [m for m in required if m not in src]
    if missing:
        raise MobilePredictContractError(f"CustomPredictForm missing {missing}")
    # form pane must appear before result pane in source (stack order)
    if src.index("predict-form-pane") > src.index("predict-result-pane"):
        raise MobilePredictContractError("form pane must precede result pane in DOM order")
    return {"custom_form_ok": True, "path": str(CUSTOM_FORM.relative_to(ROOT))}


def assert_train_desktop_notice() -> dict[str, object]:
    src = TRAIN_WB.read_text(encoding="utf-8")
    if "train-desktop-notice" not in src or "desktop-first" not in src:
        raise MobilePredictContractError("TrainWorkbench missing desktop-first notice")
    if "ST-UX-04" not in src:
        raise MobilePredictContractError("TrainWorkbench missing ST-UX-04 marker")
    return {"train_notice_ok": True, "path": str(TRAIN_WB.relative_to(ROOT))}


def assert_mobile_predict_contract() -> list[dict[str, object]]:
    return [assert_custom_form_stacks(), assert_train_desktop_notice()]


def mobile_predict_manifest(*, seed: int = 42) -> dict[str, object]:
    return {
        "id": ARTEFACT_ID,
        "stress_test": STRESS_ID,
        "seed": seed,
        "min_width_px": 360,
        "checks": assert_mobile_predict_contract(),
    }
