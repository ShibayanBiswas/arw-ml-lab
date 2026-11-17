"""Intake leakage suspects — MI-15 / ST-ML-02 (ARCHITECTURE §46.1, §33)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from labcore.intake.d6_leakage import detect_leakage
from labcore.intake.pipeline import run_intake
from labcore.intake.profile import extended_profile
from labcore.integrity.target_leakage_policy import (
    MI15_RULE,
    NEAR_PERFECT_CLF_ACC,
    POST_OUTCOME_RULE,
)

ARTEFACT_ID = "MI.TARGET.LEAKAGE"
STRESS_ID = "ST-ML-02"


class TargetLeakageContractError(ValueError):
    """Raised when MI-15 offline kit contract is violated."""


def _leakage_context(
    df: pd.DataFrame,
    *,
    y_col: str,
) -> tuple[dict, dict, list, dict, dict]:
    profile = extended_profile(df)
    roles: dict[str, dict] = {}
    for name in df.columns:
        if name == y_col:
            roles[name] = {"role": "target", "included": True}
        else:
            roles[name] = {"role": "feature", "included": True}
    targets = [{"column": y_col}]
    d1: dict = {}
    family = {"proposed": "supervised_non_sequential"}
    return profile, roles, targets, d1, family


def assert_mi15_near_perfect_predictor(*, seed: int = 42) -> dict[str, object]:
    """MI-15: near-perfect single-feature stump flags ``near_perfect_predictor``."""
    rng = np.random.default_rng(seed)
    n = 240
    y = rng.integers(0, 2, size=n)
    noisy = y.copy()
    flip_n = max(1, int(n * (1 - NEAR_PERFECT_CLF_ACC)))
    noisy[:flip_n] = 1 - noisy[:flip_n]
    df = pd.DataFrame({"y": y, "leaky_stump": noisy, "x0": rng.normal(size=n)})
    profile, roles, targets, d1, family = _leakage_context(df, y_col="y")
    suspects = detect_leakage(df, profile, roles, targets, d1, family)
    hit = next((s for s in suspects if s.get("column") == "leaky_stump"), None)
    if hit is None or hit.get("rule") != "near_perfect_predictor":
        raise TargetLeakageContractError(
            "MI-15: leaky_stump must be flagged near_perfect_predictor",
        )
    acc = float((hit.get("evidence") or {}).get("stump_accuracy", 0))
    if acc < NEAR_PERFECT_CLF_ACC:
        raise TargetLeakageContractError(
            f"MI-15: expected stump_accuracy ≥ {NEAR_PERFECT_CLF_ACC}, got {acc}",
        )
    return {
        "mi_rule": MI15_RULE,
        "column": "leaky_stump",
        "rule": hit["rule"],
        "stump_accuracy": acc,
        "seed": seed,
    }


def assert_mi15_post_outcome_name(*, seed: int = 42) -> dict[str, object]:
    """MI-15: post-outcome column names surface ``post_outcome_name`` suspects."""
    rng = np.random.default_rng(seed)
    n = 80
    df = pd.DataFrame(
        {
            "y": rng.normal(size=n),
            "outcome_revenue": rng.normal(size=n),
            "feature_a": rng.normal(size=n),
        }
    )
    profile, roles, targets, d1, family = _leakage_context(df, y_col="y")
    suspects = detect_leakage(df, profile, roles, targets, d1, family)
    hit = next((s for s in suspects if s.get("column") == "outcome_revenue"), None)
    if hit is None or hit.get("rule") != POST_OUTCOME_RULE:
        raise TargetLeakageContractError("MI-15: outcome_* column must trigger post_outcome_name")
    return {
        "mi_rule": MI15_RULE,
        "column": "outcome_revenue",
        "rule": POST_OUTCOME_RULE,
        "severity": hit.get("severity"),
        "seed": seed,
    }


def assert_mi15_intake_excludes_critical_leak(*, seed: int = 42) -> dict[str, object]:
    """MI-15: critical transform-of-target features are excluded before training."""
    rng = np.random.default_rng(seed)
    n = 120
    y = rng.integers(0, 2, size=n)
    df = pd.DataFrame(
        {
            "target": y,
            "leak_exact": y,
            "feat_ok": rng.normal(size=n),
        }
    )
    merged = run_intake(df)["merged"]
    roles = merged.get("roles") or {}
    leak_role = roles.get("leak_exact") or {}
    if leak_role.get("included") is not False:
        raise TargetLeakageContractError(
            "MI-15: exact target duplicate must be excluded from intake roles",
        )
    if "leakage_suspect" not in (leak_role.get("tags") or []):
        raise TargetLeakageContractError("MI-15: leak_exact must carry leakage_suspect tag")
    excluded = {e["column"]: e for e in merged.get("excluded") or []}
    if "leak_exact" not in excluded:
        raise TargetLeakageContractError("MI-15: leak_exact must appear in merged excluded list")
    reason = str(excluded["leak_exact"].get("reason_code", ""))
    if reason not in {"leakage_suspect", "duplicate"}:
        raise TargetLeakageContractError(
            f"MI-15: exclusion reason must be leakage_suspect or duplicate, got {reason!r}",
        )
    suspects = merged.get("leakage_suspects") or []
    if not any(s.get("column") == "leak_exact" for s in suspects):
        raise TargetLeakageContractError("MI-15: leak_exact must appear in leakage_suspects")
    return {
        "mi_rule": MI15_RULE,
        "excluded_column": "leak_exact",
        "reason_code": reason,
        "hard_exclude": bool(leak_role.get("hard_exclude")),
        "n_rows": n,
        "seed": seed,
    }


def assert_target_leakage_contract(*, seed: int = 42) -> list[dict[str, object]]:
    return [
        assert_mi15_near_perfect_predictor(seed=seed),
        assert_mi15_post_outcome_name(seed=seed),
        assert_mi15_intake_excludes_critical_leak(seed=seed),
    ]


def target_leakage_manifest(*, seed: int = 42) -> dict[str, object]:
    checks = assert_target_leakage_contract(seed=seed)
    return {
        "id": ARTEFACT_ID,
        "stress_test": STRESS_ID,
        "mi_rule": MI15_RULE,
        "seed": seed,
        "checks": checks,
    }