"""Data-quality integrity — MI-11 / MI-12 / ST-ML-03 (ARCHITECTURE §46.1).

- MI-11: constant and all-NaN columns dropped with a warning (recipe ``drop_constant``).
- MI-12: ambiguous day/month dates surface Intake questions or ``ambiguous_format``.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

ARTEFACT_ID = "MI.DATA.QUALITY"
MI11_RULE = "MI-11"
MI12_RULE = "MI-12"
RECIPE_MODULE = "labcore/preprocess/recipe.py"


class DataQualityContractError(ValueError):
    """Raised when MI-11/MI-12 kit contract is violated."""


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def assert_recipe_drop_constant_default() -> dict[str, str]:
    """``RecipeSpec.drop_constant`` must default to True (MI-11)."""
    from labcore.preprocess.recipe import RecipeSpec

    default = RecipeSpec()
    if not default.drop_constant:
        raise DataQualityContractError("RecipeSpec.drop_constant must default to True (MI-11)")
    path = _repo_root() / RECIPE_MODULE
    if not path.is_file():
        raise DataQualityContractError(f"missing {RECIPE_MODULE}")
    text = path.read_text(encoding="utf-8")
    if "def drop_constant_columns" not in text:
        raise DataQualityContractError(f"{RECIPE_MODULE}: missing drop_constant_columns")
    return {"recipe_module": RECIPE_MODULE, "drop_constant_default": "true"}


def assert_mi11_drops_constant_and_all_nan(*, seed: int = 42) -> dict[str, object]:
    """Exercise ``drop_constant_columns`` on a synthetic frame."""
    from labcore.preprocess.recipe import drop_constant_columns

    rng = np.random.default_rng(seed)
    df = pd.DataFrame(
        {
            "keep": rng.standard_normal(12),
            "all_nan": [np.nan] * 12,
            "const": [5] * 12,
        }
    )
    out, dropped = drop_constant_columns(df)
    expected = {"all_nan", "const"}
    if set(dropped) != expected or list(out.columns) != ["keep"]:
        raise DataQualityContractError(
            f"MI-11: expected dropped {expected!r}, got {dropped!r} columns={list(out.columns)}",
        )
    return {
        "mi_rule": MI11_RULE,
        "dropped": sorted(dropped),
        "kept_columns": list(out.columns),
        "seed": seed,
    }


def assert_mi12_ambiguous_date_intake(*, seed: int = 42) -> dict[str, object]:
    """Ambiguous dd/mm vs mm/dd dates must surface questions or ``ambiguous_format``."""
    from labcore.intake.d1_datetime import detect_datetime_index
    from labcore.intake.profile import extended_profile

    df = pd.DataFrame(
        {
            "event_date": ["01/02/2024", "03/04/2024", "05/06/2024", "07/08/2024"] * 5,
            "y": range(20),
        }
    )
    profile = extended_profile(df)
    d1 = detect_datetime_index(df, profile)
    questions = d1.get("questions") or []
    accepted = d1.get("accepted") or {}
    ambiguous_questions = any(
        "ambiguous" in q.lower() or "≤ 12" in q or "<= 12" in q for q in questions
    )
    ambiguous_flag = bool(accepted.get("ambiguous_format"))
    if not ambiguous_questions and not ambiguous_flag:
        raise DataQualityContractError(
            "MI-12: ambiguous day/month dates must produce Intake questions or ambiguous_format",
        )
    path = _repo_root() / "labcore/intake/d1_datetime.py"
    if path.is_file():
        text = path.read_text(encoding="utf-8")
        if not re.search(r"ambiguous", text, re.IGNORECASE):
            raise DataQualityContractError("d1_datetime.py must document ambiguous date handling")
    return {
        "mi_rule": MI12_RULE,
        "question_count": len(questions),
        "ambiguous_via_question": ambiguous_questions,
        "ambiguous_format_flag": ambiguous_flag,
        "seed": seed,
    }


def assert_data_quality_contract(*, seed: int = 42) -> list[dict[str, object]]:
    """Run all ST-ML-03 offline checks."""
    return [
        assert_recipe_drop_constant_default(),
        assert_mi11_drops_constant_and_all_nan(seed=seed),
        assert_mi12_ambiguous_date_intake(seed=seed),
    ]


def data_quality_manifest(*, seed: int = 42) -> dict[str, object]:
    checks = assert_data_quality_contract(seed=seed)
    return {
        "id": ARTEFACT_ID,
        "stress_test": "ST-ML-03",
        "mi_rules": [MI11_RULE, MI12_RULE],
        "seed": seed,
        "checks": checks,
    }