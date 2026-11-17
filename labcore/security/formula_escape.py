"""CSV/XLSX formula-injection escape (SEC-04 / §46.3 PV15, rule 60)."""

from __future__ import annotations

from typing import Any

# OWASP CSV injection: leading = + - @ tab CR
FORMULA_TRIGGER_PREFIXES: tuple[str, ...] = ("=", "+", "-", "@", "\t", "\r")


def is_formula_trigger(text: str) -> bool:
    return bool(text) and text[0] in FORMULA_TRIGGER_PREFIXES


def escape_formula_export_cell(value: Any) -> str:
    """Prefix risky string cells with `'` so spreadsheets treat them as text."""
    if value is None:
        return ""
    s = value if isinstance(value, str) else str(value)
    if is_formula_trigger(s):
        return "'" + s
    return s