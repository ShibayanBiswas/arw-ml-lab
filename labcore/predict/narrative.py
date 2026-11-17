"""Prediction narrative from FACTS only (§45.12) — never fabricates metrics."""

from __future__ import annotations

from typing import Any

ARTEFACT_ID = "PRED.NARRATIVE"
ALLOWED_FACT_KEYS = (
    "prediction",
    "pred_class",
    "pred_proba",
    "probabilities",
    "pred_lower_90",
    "pred_upper_90",
    "pred_interval_method",
    "confidence_level",
    "humility_action",
    "abstain",
    "ood_score",
    "flag_ood",
    "flag_out_of_range",
    "pv_codes",
    "calibration_status",
    "n_rows",
    "model_id",
    "task",
)


def _cite(key: str) -> str:
    return f"FACTS.{key}"


def prediction_narrative(facts: dict[str, Any], *, seed: int = 42) -> dict[str, Any]:
    """Deterministic explanation echoing only supplied FACTS keys/values."""
    findings: list[dict[str, Any]] = []
    citations: list[str] = ["FACTS"]

    pred = facts.get("prediction", facts.get("pred_class"))
    if pred is not None:
        findings.append(
            {
                "severity": "info",
                "text": f"Point prediction = {pred!r}",
                "citation": _cite("prediction" if "prediction" in facts else "pred_class"),
            }
        )
        citations.append(_cite("prediction" if "prediction" in facts else "pred_class"))

    if "pred_lower_90" in facts and "pred_upper_90" in facts:
        method = facts.get("pred_interval_method", "unknown")
        level = facts.get("confidence_level", 0.9)
        findings.append(
            {
                "severity": "info",
                "text": (
                    f"Interval [{facts['pred_lower_90']}, {facts['pred_upper_90']}] "
                    f"at level={level} via {method}"
                ),
                "citation": _cite("pred_lower_90"),
            }
        )
        citations.extend([_cite("pred_lower_90"), _cite("pred_upper_90")])

    if facts.get("abstain") or facts.get("humility_action") == "abstain":
        findings.append(
            {
                "severity": "warn",
                "text": "Humility abstain — prediction suppressed for review",
                "citation": _cite("humility_action"),
            }
        )
    elif facts.get("humility_action"):
        findings.append(
            {
                "severity": "info",
                "text": f"Humility action = {facts['humility_action']!r}",
                "citation": _cite("humility_action"),
            }
        )

    if facts.get("flag_ood") or (
        isinstance(facts.get("ood_score"), (int, float)) and float(facts["ood_score"]) > 3.0
    ):
        findings.append(
            {
                "severity": "warn",
                "text": f"OOD flag / score={facts.get('ood_score')!r}",
                "citation": _cite("ood_score" if "ood_score" in facts else "flag_ood"),
            }
        )

    oor = facts.get("flag_out_of_range") or []
    if isinstance(oor, list) and oor:
        findings.append(
            {
                "severity": "warn",
                "text": f"Out-of-range features: {oor}",
                "citation": _cite("flag_out_of_range"),
            }
        )

    pv = facts.get("pv_codes") or []
    if isinstance(pv, list) and pv:
        findings.append(
            {
                "severity": "info",
                "text": f"Validation codes: {pv}",
                "citation": _cite("pv_codes"),
            }
        )

    if facts.get("calibration_status"):
        findings.append(
            {
                "severity": "info",
                "text": f"Calibration status = {facts['calibration_status']!r}",
                "citation": _cite("calibration_status"),
            }
        )

    if not findings:
        present = [k for k in ALLOWED_FACT_KEYS if k in facts]
        findings.append(
            {
                "severity": "info",
                "text": f"No narrative fields beyond keys={present}",
                "citation": "FACTS",
            }
        )

    summary_bits = [f["text"] for f in findings[:3]]
    return {
        "mode": "numbers-only",
        "artefact": ARTEFACT_ID,
        "seed": seed,
        "stage": "prediction",
        "summary": "; ".join(summary_bits),
        "findings": findings,
        "citations": sorted(set(citations)),
        "apply_patch": None,
        "provider": "numbers-only",
        "confidence_explanation": next(
            (f["text"] for f in findings if "Interval" in f["text"] or "prediction" in f["text"].lower()),
            findings[0]["text"],
        ),
        "caveats": [
            f["text"] for f in findings if f["severity"] == "warn"
        ],
    }
