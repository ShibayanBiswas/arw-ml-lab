"""Leaderboard CSV/XLSX export — formula-injection safe (SEC-04 / ST-UX-02)."""

from __future__ import annotations

import csv
import io
from typing import Any

from labcore.security.formula_escape import escape_formula_export_cell as _safe_cell

_BASE_FIELDS = ("rank", "algorithm_key", "algorithm_id", "name", "library", "primary_metric")


def _leaderboard_metric_keys(rows: list[dict[str, Any]]) -> list[str]:
    metric_keys: list[str] = []
    for r in rows:
        for k in r.get("cv_mean") or {}:
            if k not in metric_keys:
                metric_keys.append(k)
    return metric_keys


def leaderboard_fieldnames(rows: list[dict[str, Any]]) -> list[str]:
    fieldnames = list(_BASE_FIELDS)
    for k in _leaderboard_metric_keys(rows):
        fieldnames.append(f"cv_mean_{k}")
        fieldnames.append(f"cv_std_{k}")
        fieldnames.append(f"test_{k}")
    return fieldnames


def flatten_leaderboard_row(r: dict[str, Any], *, metric_keys: list[str]) -> dict[str, Any]:
    flat: dict[str, Any] = {k: r.get(k) for k in _BASE_FIELDS}
    cv_mean = r.get("cv_mean") or {}
    cv_std = r.get("cv_std") or {}
    test = r.get("test") or {}
    for k in metric_keys:
        flat[f"cv_mean_{k}"] = cv_mean.get(k)
        flat[f"cv_std_{k}"] = cv_std.get(k)
        flat[f"test_{k}"] = test.get(k)
    return flat


def leaderboard_to_csv(rows: list[dict[str, Any]]) -> str:
    """Flatten cv_mean/test into columns; escape formula cells."""
    if not rows:
        return "rank,algorithm_key,name\n"
    metric_keys = _leaderboard_metric_keys(rows)
    fieldnames = leaderboard_fieldnames(rows)
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for r in rows:
        flat = flatten_leaderboard_row(r, metric_keys=metric_keys)
        writer.writerow({k: _safe_cell(v) for k, v in flat.items()})
    return buf.getvalue()


def leaderboard_to_xlsx_bytes(rows: list[dict[str, Any]]) -> bytes:
    """XLSX leaderboard (openpyxl write + SEC-04 cell escape)."""
    from labcore.security.upload_guard import ensure_defused_xml_stdlib

    ensure_defused_xml_stdlib()
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    assert ws is not None
    ws.title = "leaderboard"
    metric_keys = _leaderboard_metric_keys(rows)
    fieldnames = leaderboard_fieldnames(rows) if rows else list(_BASE_FIELDS)
    ws.append([_safe_cell(h) for h in fieldnames])
    for r in rows:
        flat = flatten_leaderboard_row(r, metric_keys=metric_keys)
        ws.append([_safe_cell(flat.get(k)) for k in fieldnames])
    bio = io.BytesIO()
    wb.save(bio)
    return bio.getvalue()
