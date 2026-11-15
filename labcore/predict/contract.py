"""Feature contract builder + schema validation (ARCHITECTURE §45.2)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "docs" / "contracts" / "feature_contract.schema.json"

# Identifier-like heuristics — never store cell values for these (§45.2 / MI hardening)
_ID_NAME_HINTS = ("id", "uuid", "ssn", "email", "phone", "customer", "account", "pan", "aadhaar")


def looks_identifier(name: str, series: pd.Series) -> bool:
    low = name.lower()
    if any(h in low for h in _ID_NAME_HINTS):
        return True
    n = len(series)
    if n == 0:
        return False
    nunq = int(series.nunique(dropna=True))
    return nunq >= max(50, int(0.9 * n)) and series.dtype == object


# Back-compat alias used by older call sites
_looks_identifier = looks_identifier


def build_feature_contract(
    X_train: pd.DataFrame,
    *,
    dataset_id: str,
    task: str,
    target: str | None,
    seed: int = 42,
    model_id: str | None = None,
) -> dict[str, Any]:
    """Build a §45.2 feature contract from the training split only (no test leakage)."""
    features: list[dict[str, Any]] = []
    id_columns: list[str] = []
    for col in X_train.columns:
        s = X_train[col]
        if _looks_identifier(str(col), s):
            id_columns.append(str(col))
            features.append(
                {
                    "name": str(col),
                    "kind": "identifier_like",
                    "dtype": str(s.dtype),
                    "nullable": bool(s.isna().any()),
                    "role": "excluded_by_default",
                    # Never store values of identifier-like columns
                }
            )
            continue
        if pd.api.types.is_bool_dtype(s) or set(s.dropna().unique().tolist()) <= {
            0,
            1,
        }:
            features.append(
                {
                    "name": str(col),
                    "kind": "boolean",
                    "dtype": str(s.dtype),
                    "nullable": bool(s.isna().any()),
                    "mode": str(s.mode(dropna=True).iloc[0]) if s.notna().any() else None,
                    "role": "feature",
                }
            )
        elif pd.api.types.is_numeric_dtype(s):
            vals = pd.to_numeric(s, errors="coerce")
            features.append(
                {
                    "name": str(col),
                    "kind": "numeric",
                    "dtype": str(s.dtype),
                    "nullable": bool(vals.isna().any()),
                    "min": float(vals.min()) if vals.notna().any() else None,
                    "max": float(vals.max()) if vals.notna().any() else None,
                    "median": float(vals.median()) if vals.notna().any() else None,
                    "p01": float(vals.quantile(0.01)) if vals.notna().any() else None,
                    "p99": float(vals.quantile(0.99)) if vals.notna().any() else None,
                    "integer": bool(np.issubdtype(vals.dropna().dtype, np.integer))
                    if vals.notna().any()
                    else False,
                    "role": "feature",
                }
            )
        else:
            cats = [str(v) for v in s.dropna().astype(str).unique().tolist()]
            mode = str(s.mode(dropna=True).iloc[0]) if s.notna().any() else None
            features.append(
                {
                    "name": str(col),
                    "kind": "categorical",
                    "dtype": str(s.dtype),
                    "nullable": bool(s.isna().any()),
                    "categories": cats[:64],
                    "categories_truncated": len(cats) > 64,
                    "n_categories": len(cats),
                    "mode": mode,
                    "role": "feature",
                }
            )

    contract: dict[str, Any] = {
        "contract_version": "1.0",
        "dataset_id": dataset_id,
        "task": task,
        "target": target,
        "id_columns": id_columns,
        "time_column": None,
        "series_column": None,
        "frequency": None,
        "horizon_max": None,
        "seed": int(seed),
        "n_train_rows": int(len(X_train)),
        "features": features,
        "derived_features": [],
        "library_versions": {},
    }
    if model_id:
        contract["model_id"] = model_id
    return contract


def validate_feature_contract(contract: dict[str, Any]) -> list[str]:
    """Validate against the JSON Schema; return a list of error messages (empty = ok)."""
    import jsonschema

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    return [e.message for e in validator.iter_errors(contract)]


def assert_no_identifier_values(contract: dict[str, Any]) -> None:
    for feat in contract.get("features") or []:
        if feat.get("kind") == "identifier_like":
            for banned in ("categories", "min", "max", "median", "mode", "values", "sample"):
                if banned in feat and feat[banned] not in (None, [], {}):
                    raise ValueError(f"identifier_like feature must not store {banned}")
