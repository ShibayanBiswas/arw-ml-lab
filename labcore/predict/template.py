"""Downloadable prediction templates from a feature contract (§45.2 / §45.5)."""

from __future__ import annotations

import io
from typing import Any, Literal

import pandas as pd

from labcore.train.export import _safe_cell


def _template_feature_names(
    contract: dict[str, Any],
    *,
    feature_names: list[str] | None = None,
) -> list[str]:
    if feature_names is not None:
        return list(feature_names)
    names: list[str] = []
    for feat in contract.get("features") or []:
        if feat.get("kind") == "identifier_like":
            continue
        if feat.get("role") == "excluded_by_default":
            continue
        names.append(str(feat["name"]))
    return names


def _default_value(feat: dict[str, Any]) -> Any:
    kind = feat.get("kind")
    if kind == "boolean":
        mode = feat.get("mode")
        if mode is None:
            return False
        s = str(mode).strip().lower()
        return s in {"true", "1", "yes", "y", "t"}
    if kind == "categorical":
        return feat.get("mode")
    if kind == "numeric":
        if feat.get("median") is not None:
            return feat["median"]
        if feat.get("min") is not None:
            return feat["min"]
        return 0
    return None


def sample_row_from_contract(
    contract: dict[str, Any],
    *,
    feature_names: list[str] | None = None,
) -> dict[str, Any]:
    """One default row (medians / modes) — never includes identifier values."""
    by_name = {str(f["name"]): f for f in (contract.get("features") or [])}
    names = _template_feature_names(contract, feature_names=feature_names)
    row: dict[str, Any] = {}
    for name in names:
        feat = by_name.get(name, {"kind": "numeric", "name": name})
        if feat.get("kind") == "identifier_like":
            continue
        row[name] = _default_value(feat)
    return row


def template_dataframe(
    contract: dict[str, Any],
    *,
    feature_names: list[str] | None = None,
    n_example_rows: int = 1,
) -> pd.DataFrame:
    """Empty-ish template: header + optional default example row(s)."""
    names = _template_feature_names(contract, feature_names=feature_names)
    if n_example_rows <= 0:
        return pd.DataFrame(columns=names)
    row = sample_row_from_contract(contract, feature_names=names)
    rows = [row for _ in range(n_example_rows)]
    return pd.DataFrame(rows, columns=names)


def template_csv_bytes(
    contract: dict[str, Any],
    *,
    feature_names: list[str] | None = None,
    n_example_rows: int = 1,
) -> bytes:
    df = template_dataframe(contract, feature_names=feature_names, n_example_rows=n_example_rows)
    buf = io.StringIO()
    # Formula-safe cells (SEC-04 / PV15 on export)
    safe = df.map(lambda v: _safe_cell(v))
    safe.to_csv(buf, index=False)
    return buf.getvalue().encode("utf-8")


def template_xlsx_bytes(
    contract: dict[str, Any],
    *,
    feature_names: list[str] | None = None,
    n_example_rows: int = 1,
) -> bytes:
    from labcore.security.upload_guard import ensure_defused_xml_stdlib

    ensure_defused_xml_stdlib()
    from openpyxl import Workbook

    df = template_dataframe(contract, feature_names=feature_names, n_example_rows=n_example_rows)
    wb = Workbook()
    ws = wb.active
    assert ws is not None
    ws.title = "predict"
    headers = list(df.columns)
    ws.append([_safe_cell(h) for h in headers])
    for _, row in df.iterrows():
        ws.append([_safe_cell(row[c]) for c in headers])
    bio = io.BytesIO()
    wb.save(bio)
    return bio.getvalue()


def predictions_to_safe_csv(df: pd.DataFrame) -> bytes:
    """Score-result CSV with formula-injection escaping (SEC-04)."""
    buf = io.StringIO()
    safe = df.map(lambda v: _safe_cell(v))
    safe.to_csv(buf, index=False)
    return buf.getvalue().encode("utf-8")


TemplateFormat = Literal["csv", "xlsx"]
