"""Orchestrate D1–D8 → merged intake proposal — ARCHITECTURE §33.1."""

from __future__ import annotations

from typing import Any

import pandas as pd

from labcore.intake.d1_datetime import detect_datetime_index
from labcore.intake.d2_frequency import infer_frequency
from labcore.intake.d3_roles import detect_roles
from labcore.intake.d4_family import infer_family
from labcore.intake.d5_targets import recommend_targets_features
from labcore.intake.d6_leakage import detect_leakage
from labcore.intake.d7_diff import schema_diff
from labcore.intake.d8_drift import drift_report
from labcore.intake.profile import extended_profile
from labcore.intake.schemas import IntakeProposal
from labcore.intake.validator import validate_proposal


_DETECTOR_SAMPLE_CAP = 20_000


def run_intake(
    df: pd.DataFrame,
    *,
    parent_df: pd.DataFrame | None = None,
    dataset_name: str | None = None,
) -> dict[str, Any]:
    """Run rule-based intake; returns detector_output, merged proposal, validator_report."""
    _ = dataset_name
    # §33.2: detectors run on ≤20k sample where stated; keep full n_rows in profile
    work = df
    if len(df) > _DETECTOR_SAMPLE_CAP:
        # Stride sample (O(k)) — avoid full-frame shuffle on multi-million rows
        step = max(1, len(df) // _DETECTOR_SAMPLE_CAP)
        work = df.iloc[::step].head(_DETECTOR_SAMPLE_CAP).reset_index(drop=True)
    profile = extended_profile(work)
    profile["n_rows"] = int(len(df))
    profile["sampled"] = bool(len(df) > _DETECTOR_SAMPLE_CAP)
    d1 = detect_datetime_index(work, profile)
    # drop internal parsed map from serialisable output
    d1_public = {k: v for k, v in d1.items() if not k.startswith("_")}
    d2 = infer_frequency(work, d1, profile)
    roles = detect_roles(work, profile, d1, d2)
    family = infer_family(work, profile, d1, d2, roles)
    tf = recommend_targets_features(work, profile, roles, family, d2)
    leakage = detect_leakage(work, profile, roles, tf["targets"], d1, family)

    # tag leakage on roles
    for s in leakage:
        col = s.get("column")
        if col and col in roles:
            roles[col].setdefault("tags", []).append("leakage_suspect")
            if s.get("severity") in {"high", "critical"}:
                roles[col]["included"] = False

    excluded = []
    for name, r in roles.items():
        if not r.get("included") or r.get("hard_exclude"):
            reason = r["role"].split(":")[0]
            if reason.startswith("duplicate_of"):
                reason = "duplicate"
            if "high_missing" in r.get("tags", []):
                reason = "high_missing"
            if "leakage_suspect" in r.get("tags", []):
                reason = "leakage_suspect"
            excluded.append(
                {
                    "column": name,
                    "reason_code": reason
                    if reason
                    in {
                        "row_id",
                        "constant",
                        "near_constant",
                        "duplicate",
                        "text",
                        "pii",
                        "high_missing",
                        "leakage_suspect",
                        "time_index",
                        "entity_id",
                        "other",
                    }
                    else "other",
                    "detail": "; ".join(r.get("reasons") or []),
                }
            )

    questions = list(d1.get("questions") or [])
    if family.get("preselected") is False:
        questions.append("Please choose the problem family (confidence below threshold).")

    time_index = None
    if d1.get("accepted"):
        acc = d1["accepted"]
        time_index = {
            "column": acc.get("column"),
            "format": acc.get("format"),
            "timezone": acc.get("timezone", "Asia/Kolkata"),
            "composite_of": acc.get("composite_of"),
            "confidence": acc.get("confidence"),
            "reasons": acc.get("reasons"),
            "ambiguous_format": acc.get("ambiguous_format"),
        }

    frequency = None
    if d2.get("alias"):
        frequency = {
            "alias": d2.get("alias"),
            "calendar": d2.get("calendar"),
            "regularity": d2.get("regularity"),
            "seasonal_periods": d2.get("seasonal_periods"),
            "confidence": d2.get("confidence"),
        }

    scores = family.get("scores") or {}
    conf_overall = float(max(scores.values()) if scores else 0.0)

    merged = IntakeProposal(
        time_index=time_index,
        entity_column=d1.get("entity"),
        frequency=frequency,
        family={
            "proposed": family.get("proposed"),
            "financial": family.get("financial"),
            "scores": scores,
            "reasons": family.get("reasons"),
            "preselected": family.get("preselected"),
        },
        task=tf.get("task"),
        targets=tf.get("targets") or [],
        features=tf.get("features") or [],
        excluded=excluded,
        leakage_suspects=leakage,
        cv_recommendation=_cv_rec(family),
        horizon=tf.get("horizon"),
        questions_for_user=questions,
        confidence_overall=conf_overall,
        roles=roles,
        mode="rule_based",
        rules_version="intake-1.0",
    )

    report = validate_proposal(merged, column_names=set(work.columns), roles=roles)

    detector_output = {
        "profile_summary": {
            "n_rows": profile["n_rows"],
            "n_cols": profile["n_cols"],
            "sampled": profile["sampled"],
            "duplicate_row_share": profile["duplicate_row_share"],
        },
        "d1": d1_public,
        "d2": d2,
        "d3_roles": roles,
        "d4_family": family,
        "d5": {"targets": tf.get("targets"), "task": tf.get("task")},
        "d6_leakage": leakage,
    }

    versioning: dict[str, Any] | None = None
    if parent_df is not None:
        diff = schema_diff(parent_df, df)
        drift = drift_report(parent_df, df)
        versioning = {"diff": diff, "drift": drift}

    return {
        "detector_output": detector_output,
        "llm_output": None,
        "merged": merged.model_dump(),
        "validator_report": report,
        "versioning": versioning,
        "rules_version": "intake-1.0",
        "confidence_overall": conf_overall,
    }


def _cv_rec(family: dict[str, Any]) -> dict[str, Any]:
    if family.get("financial") or family.get("proposed") == "supervised_sequential":
        return {
            "scheme": "purged_kfold",
            "params": {"k": 5, "embargo": 0.01},
            "reason": "financial_sequential",
        }
    if family.get("proposed") == "time_series":
        return {
            "scheme": "timeseries_split",
            "params": {"n_splits": 5},
            "reason": "time_series",
        }
    return {
        "scheme": "stratified_kfold",
        "params": {"k": 5, "n_repeats": 2, "seed": 42},
        "reason": "default_supervised",
    }
