"""Offline artefact PRED.HUMILITY — ST-FEAT-01 (ARCHITECTURE §45 / §46.5)."""

from __future__ import annotations

import numpy as np

from labcore.predict.humility import (
    ARTEFACT_ID,
    STRESS_ID,
    HumilityPolicy,
    apply_humility_batch,
    apply_humility_row,
    escalate_actions,
    suppress_prediction_if_abstain,
)


class HumilityContractError(ValueError):
    """Raised when PRED.HUMILITY offline kit contract is violated."""


def assert_escalate_precedence() -> dict[str, object]:
    if escalate_actions([]) is not None:
        raise HumilityContractError("empty actions must yield None")
    if escalate_actions(["warn"]) != "warn":
        raise HumilityContractError("single warn")
    if escalate_actions(["warn", "review"]) != "review":
        raise HumilityContractError("review beats warn")
    if escalate_actions(["warn", "review", "abstain"]) != "abstain":
        raise HumilityContractError("abstain beats review")
    return {"escalate_ok": True}


def assert_ood_warn_default(*, seed: int = 42) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    score = float(3.5 + rng.random())
    out = apply_humility_row(ood_score=score)
    if not out["flag_ood"] or out["humility_action"] != "warn":
        raise HumilityContractError("default OOD must warn")
    if out["abstain"] or out["prediction_suppressed"]:
        raise HumilityContractError("default OOD must not abstain")
    return {"ood_score": score, "action": out["humility_action"], "seed": seed}


def assert_out_of_range_flag() -> dict[str, object]:
    out = apply_humility_row(
        ood_score=0.1,
        flag_out_of_range=["age"],
        policy=HumilityPolicy(action_out_of_range="review"),
    )
    if "out_of_range" not in out["humility_triggers"]:
        raise HumilityContractError("missing out_of_range trigger")
    if out["humility_action"] != "review" or not out["needs_human_review"]:
        raise HumilityContractError("out_of_range review action")
    return {"triggers": out["humility_triggers"], "action": out["humility_action"]}


def assert_wide_interval_abstain(*, seed: int = 42) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    scale = 10.0
    width = scale * (1.5 + 0.1 * float(rng.random()))
    out = apply_humility_row(
        ood_score=0.0,
        interval_lower=0.0,
        interval_upper=width,
        training_target_scale=scale,
        policy=HumilityPolicy(action_wide_interval="abstain", interval_width_ratio_max=1.0),
    )
    if "wide_interval" not in out["humility_triggers"]:
        raise HumilityContractError("wide_interval not triggered")
    if out["humility_action"] != "abstain" or not out["prediction_suppressed"]:
        raise HumilityContractError("wide interval must abstain under policy")
    suppressed = suppress_prediction_if_abstain(42.0, out)
    if suppressed is not None:
        raise HumilityContractError("abstain must suppress prediction value")
    return {
        "interval_width": out["interval_width"],
        "ratio": out["interval_width_ratio"],
        "action": out["humility_action"],
        "seed": seed,
    }


def assert_clean_row_passthrough() -> dict[str, object]:
    out = apply_humility_row(ood_score=0.5, flag_out_of_range=[])
    if out["humility_action"] is not None or out["humility_triggers"]:
        raise HumilityContractError("clean row must have no humility action")
    if suppress_prediction_if_abstain(7, out) != 7:
        raise HumilityContractError("clean row must keep prediction")
    return {"action": None, "passthrough": True}


def assert_batch_seed42(*, seed: int = 42) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    rows = [
        {"ood_score": 0.2},
        {"ood_score": 4.0 + float(rng.random()), "flag_out_of_range": []},
        {
            "ood_score": 0.1,
            "pred_lower": 0.0,
            "pred_upper": 25.0,
            "training_target_scale": 10.0,
        },
    ]
    pol = HumilityPolicy(
        action_ood="warn",
        action_wide_interval="review",
        interval_width_ratio_max=1.0,
    )
    results = apply_humility_batch(rows, policy=pol)
    if len(results) != 3:
        raise HumilityContractError("batch length")
    if results[0]["humility_action"] is not None:
        raise HumilityContractError("row0 clean")
    if results[1]["humility_action"] != "warn":
        raise HumilityContractError("row1 ood warn")
    if results[2]["humility_action"] != "review":
        raise HumilityContractError("row2 wide → review")
    return {"n": 3, "actions": [r["humility_action"] for r in results], "seed": seed}


def assert_humility_contract(*, seed: int = 42) -> list[dict[str, object]]:
    return [
        assert_escalate_precedence(),
        assert_ood_warn_default(seed=seed),
        assert_out_of_range_flag(),
        assert_wide_interval_abstain(seed=seed),
        assert_clean_row_passthrough(),
        assert_batch_seed42(seed=seed),
    ]


def humility_manifest(*, seed: int = 42) -> dict[str, object]:
    checks = assert_humility_contract(seed=seed)
    return {
        "id": ARTEFACT_ID,
        "stress_test": STRESS_ID,
        "seed": seed,
        "actions": ["warn", "abstain", "review"],
        "checks": checks,
    }
