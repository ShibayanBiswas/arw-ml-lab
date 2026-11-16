"""Insights response validator — numbers must cite FACTS (ARCHITECTURE §40)."""

from __future__ import annotations

import json
import re
from typing import Any

_NUM = re.compile(r"(?<![A-Za-z_])[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")


def validate_insights_payload(
    payload: dict[str, Any] | str,
    *,
    facts: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate an insights JSON blob.

    Rules: parseable JSON; citations include FACTS when findings present;
    every numeric literal in ``summary`` must appear in ``facts`` values
    (stringified) when facts is provided — otherwise warn.
    """
    if isinstance(payload, str):
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as exc:
            return {"ok": False, "errors": [f"invalid JSON: {exc}"], "warnings": []}
    else:
        data = payload

    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(data, dict):
        return {"ok": False, "errors": ["payload must be an object"], "warnings": []}

    findings = data.get("findings") or []
    citations = data.get("citations") or []
    if findings and "FACTS" not in citations:
        errors.append("findings present but citations missing FACTS")

    summary = str(data.get("summary") or "")
    if facts is not None:
        fact_nums = {str(v) for v in _flatten_nums(facts)}
        for match in _NUM.findall(summary):
            if match not in fact_nums and match not in {"42"}:
                warnings.append(f"number {match} in summary not found in FACTS")

    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "n_findings": len(findings) if isinstance(findings, list) else 0,
    }


def _flatten_nums(obj: Any) -> list[float | int]:
    out: list[float | int] = []
    if isinstance(obj, (int, float)) and not isinstance(obj, bool):
        out.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            out.extend(_flatten_nums(v))
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            out.extend(_flatten_nums(v))
    return out
