"""Prediction humility rules — ST-FEAT-01 / ARCHITECTURE §45 + §46.5.

Per-row actions for OOD, out-of-range inputs, and wide prediction intervals.
Configurable: warn | abstain | review (route to human). Thin policy only —
OOD scores and range flags come from validate/score; this module never refits.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal

HumilityAction = Literal["warn", "abstain", "review"]

ARTEFACT_ID = "PRED.HUMILITY"
STRESS_ID = "ST-FEAT-01"

_ACTION_RANK: dict[HumilityAction, int] = {"warn": 1, "review": 2, "abstain": 3}


@dataclass(frozen=True)
class HumilityPolicy:
    """Defaults match DataRobot-style humility: warn on flags; abstain opt-in."""

    ood_z_threshold: float = 3.0
    interval_width_ratio_max: float = 1.0
    action_ood: HumilityAction = "warn"
    action_out_of_range: HumilityAction = "warn"
    action_wide_interval: HumilityAction = "warn"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def escalate_actions(actions: list[HumilityAction]) -> HumilityAction | None:
    """abstain beats review beats warn; empty → None (no humility action)."""
    if not actions:
        return None
    return max(actions, key=lambda a: _ACTION_RANK[a])


def apply_humility_row(
    *,
    ood_score: float = 0.0,
    flag_ood: bool | None = None,
    flag_out_of_range: list[str] | None = None,
    interval_lower: float | None = None,
    interval_upper: float | None = None,
    training_target_scale: float | None = None,
    policy: HumilityPolicy | None = None,
) -> dict[str, Any]:
    """Evaluate one prediction row; never mutates model or calls fit."""
    pol = policy or HumilityPolicy()
    oor = list(flag_out_of_range or [])
    ood_flag = bool(flag_ood) if flag_ood is not None else float(ood_score) > pol.ood_z_threshold
    if float(ood_score) > pol.ood_z_threshold:
        ood_flag = True

    triggers: list[str] = []
    chosen: list[HumilityAction] = []

    if ood_flag:
        triggers.append("ood")
        chosen.append(pol.action_ood)
    if oor:
        triggers.append("out_of_range")
        chosen.append(pol.action_out_of_range)

    interval_width: float | None = None
    width_ratio: float | None = None
    if interval_lower is not None and interval_upper is not None:
        interval_width = float(interval_upper) - float(interval_lower)
        scale = float(training_target_scale) if training_target_scale else None
        if scale is not None and scale > 0 and interval_width / scale > pol.interval_width_ratio_max:
            triggers.append("wide_interval")
            chosen.append(pol.action_wide_interval)
            width_ratio = interval_width / scale

    action = escalate_actions(chosen)
    return {
        "flag_ood": ood_flag,
        "ood_score": float(ood_score),
        "flag_out_of_range": oor,
        "interval_width": interval_width,
        "interval_width_ratio": width_ratio,
        "humility_triggers": triggers,
        "humility_action": action,
        "abstain": action == "abstain",
        "needs_human_review": action == "review",
        "prediction_suppressed": action == "abstain",
        "policy": pol.to_dict(),
    }


def apply_humility_batch(
    rows: list[dict[str, Any]],
    *,
    policy: HumilityPolicy | None = None,
    training_target_scale: float | None = None,
) -> list[dict[str, Any]]:
    """Apply humility to a list of row dicts (keys: ood_score, flags, intervals)."""
    pol = policy or HumilityPolicy()
    out: list[dict[str, Any]] = []
    for row in rows:
        out.append(
            apply_humility_row(
                ood_score=float(row.get("ood_score", 0.0)),
                flag_ood=row.get("flag_ood"),
                flag_out_of_range=list(row.get("flag_out_of_range") or []),
                interval_lower=row.get("pred_lower") if "pred_lower" in row else row.get("interval_lower"),
                interval_upper=row.get("pred_upper") if "pred_upper" in row else row.get("interval_upper"),
                training_target_scale=training_target_scale
                if training_target_scale is not None
                else row.get("training_target_scale"),
                policy=pol,
            )
        )
    return out


def suppress_prediction_if_abstain(
    prediction: Any,
    humility: dict[str, Any],
) -> Any:
    """Return None when humility abstains; otherwise the original prediction."""
    if humility.get("prediction_suppressed"):
        return None
    return prediction
