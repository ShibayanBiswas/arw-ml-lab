"""Binary decision threshold from the saved contract (§45.4 pred_threshold)."""

from __future__ import annotations

from typing import Any


def pred_threshold_from_contract(feature_contract: dict[str, Any] | None) -> float | None:
    """Return the training decision threshold when recorded; else None."""
    contract = feature_contract or {}
    for key in ("pred_threshold", "decision_threshold", "threshold"):
        if contract.get(key) is not None:
            try:
                return float(contract[key])
            except (TypeError, ValueError):
                pass
    unc = contract.get("uncertainty") or {}
    if isinstance(unc, dict) and unc.get("pred_threshold") is not None:
        try:
            return float(unc["pred_threshold"])
        except (TypeError, ValueError):
            pass
    return None
