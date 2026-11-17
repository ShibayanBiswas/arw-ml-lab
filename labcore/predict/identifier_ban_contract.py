"""Feature-contract identifier ban — SEC-09 / §45.2 / ST-PRIV-01.

``identifier_like`` features must never store cell values in the contract JSON.
"""

from __future__ import annotations

import json
from pathlib import Path

from labcore.predict.contract import assert_no_identifier_values

ARTEFACT_ID = "SEC.FEATURE_CONTRACT.IDENTIFIER"
BANNED_VALUE_KEYS: tuple[str, ...] = (
    "categories",
    "min",
    "max",
    "median",
    "mode",
    "values",
    "sample",
)


class IdentifierBanContractError(ValueError):
    """Raised when a feature contract stores banned identifier values."""


def assert_identifier_ban_on_contract(contract: dict[str, object]) -> None:
    """Schema-agnostic guard used at training save and in kit scans."""
    try:
        assert_no_identifier_values(contract)
    except ValueError as exc:
        raise IdentifierBanContractError(str(exc)) from exc
    for feat in contract.get("features") or []:
        if not isinstance(feat, dict) or feat.get("kind") != "identifier_like":
            continue
        for key in BANNED_VALUE_KEYS:
            val = feat.get(key)
            if val not in (None, [], {}):
                raise IdentifierBanContractError(
                    f"identifier_like {feat.get('name')!r} must not store {key}"
                )


def scan_predict_manifest_contracts(
    manifest_path: Path | None = None,
    *,
    root: Path | None = None,
) -> list[dict[str, str]]:
    """Scan every contract referenced in ``predict_manifest.json``."""
    base = root or Path(__file__).resolve().parents[2]
    path = manifest_path or (base / "data" / "samples" / "predict" / "predict_manifest.json")
    if not path.is_file():
        msg = f"predict manifest missing: {path}"
        raise IdentifierBanContractError(msg)
    manifest = json.loads(path.read_text(encoding="utf-8"))
    entries = manifest.get("files") or manifest.get("datasets") or []
    checked: list[dict[str, str]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        rel = entry.get("feature_contract") or entry.get("contract")
        if not rel:
            continue
        contract_path = (base / str(rel)).resolve()
        if not contract_path.is_file():
            contract_path = base / "data" / "samples" / "predict" / Path(str(rel)).name
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        assert_identifier_ban_on_contract(contract)
        checked.append({"dataset": str(entry.get("name") or entry.get("dataset_id") or rel), "contract": str(rel)})
    return checked


def identifier_ban_manifest(*, seed: int = 42) -> dict[str, object]:
    return {
        "id": ARTEFACT_ID,
        "seed": seed,
        "banned_value_keys": list(BANNED_VALUE_KEYS),
        "contracts_checked": scan_predict_manifest_contracts(),
    }