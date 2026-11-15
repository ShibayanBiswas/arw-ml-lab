"""Hard-rule validator — ARCHITECTURE §33.9 (rule-based path)."""

from __future__ import annotations

from typing import Any

from labcore.intake.schemas import HARD_EXCLUDE_REASONS, IntakeProposal


def validate_proposal(
    proposal: IntakeProposal | dict[str, Any],
    *,
    column_names: set[str],
    roles: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    data = proposal.model_dump() if isinstance(proposal, IntakeProposal) else dict(proposal)
    errors: list[str] = []
    warnings: list[str] = []

    for feat in data.get("features") or []:
        col = feat.get("column")
        if col and col not in column_names and col != "__derived__":
            errors.append(f"unknown_feature:{col}")
        role_meta = roles.get(col or "", {})
        if role_meta.get("hard_exclude"):
            errors.append(f"hard_exclude_as_feature:{col}")
        reason = next(
            (e.get("reason_code") for e in (data.get("excluded") or []) if e.get("column") == col),
            None,
        )
        if reason in HARD_EXCLUDE_REASONS:
            errors.append(f"excluded_reason_as_feature:{col}:{reason}")

    for t in data.get("targets") or []:
        col = t.get("column")
        if col and col not in column_names and col != "__derived__":
            errors.append(f"unknown_target:{col}")
        if col and roles.get(col, {}).get("hard_exclude"):
            errors.append(f"hard_exclude_as_target:{col}")
        if col and str(roles.get(col, {}).get("role", "")).startswith("price_"):
            if not t.get("derived"):
                errors.append(f"raw_price_as_target:{col}")

    hz = data.get("horizon") or {}
    if hz.get("h_max") is not None and hz.get("h_default") is not None:
        if int(hz["h_default"]) > int(hz["h_max"]):
            errors.append("h_default_gt_h_max")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
    }


def apply_overrides(
    merged: dict[str, Any],
    overrides: dict[str, Any],
    roles: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Merge user overrides; never clear hard_exclude without removing from features."""
    out = dict(merged)
    if "family" in overrides:
        out.setdefault("family", {})
        out["family"] = {**out["family"], **overrides["family"]}
    if "targets" in overrides:
        out["targets"] = overrides["targets"]
    if "features" in overrides:
        out["features"] = overrides["features"]
    if "roles" in overrides:
        for col, patch in overrides["roles"].items():
            if col in roles and roles[col].get("hard_exclude") and patch.get("included") is True:
                # leave hard exclude; validator will 422 on confirm
                pass
            out.setdefault("roles", {})
            out["roles"][col] = {**out.get("roles", {}).get(col, {}), **patch}
    if "time_index" in overrides:
        out["time_index"] = overrides["time_index"]
    out["user_overrides"] = overrides
    return out


def confirm_guard(merged: dict[str, Any], roles: dict[str, dict[str, Any]]) -> None:
    """Raise ValueError suitable for HTTP 422 if hard-excluded used as feature."""
    overrides = merged.get("user_overrides") or {}
    role_overrides = overrides.get("roles") or {}
    for col, patch in role_overrides.items():
        if patch.get("included") is True and (
            roles.get(col, {}).get("hard_exclude") or not roles.get(col, {}).get("included", True)
        ):
            if roles.get(col, {}).get("hard_exclude") or roles.get(col, {}).get("role") in {
                "row_id",
                "pii",
                "text",
                "constant",
                "time_index",
                "entity_id",
            }:
                raise ValueError(f"hard-excluded column cannot be confirmed as a feature: {col}")
    for feat in merged.get("features") or []:
        col = feat.get("column")
        if not col:
            continue
        if roles.get(col, {}).get("hard_exclude"):
            # allowed only if explicitly still listed after user kept hard exclude out
            if role_overrides.get(col, {}).get("included") is True:
                raise ValueError(f"hard-excluded column cannot be a feature: {col}")
