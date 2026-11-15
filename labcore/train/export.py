"""Leaderboard CSV export — formula-injection safe (SEC-04)."""

from __future__ import annotations

import csv
import io
from typing import Any


def _safe_cell(value: Any) -> str:
    s = "" if value is None else str(value)
    if s and s[0] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + s
    return s


def leaderboard_to_csv(rows: list[dict[str, Any]]) -> str:
    """Flatten cv_mean/test into columns; escape formula cells."""
    if not rows:
        return "rank,algorithm_key,name\n"
    metric_keys: list[str] = []
    for r in rows:
        for k in r.get("cv_mean") or {}:
            if k not in metric_keys:
                metric_keys.append(k)
    fieldnames = ["rank", "algorithm_key", "algorithm_id", "name", "library", "primary_metric"]
    for k in metric_keys:
        fieldnames.append(f"cv_mean_{k}")
        fieldnames.append(f"cv_std_{k}")
        fieldnames.append(f"test_{k}")
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for r in rows:
        flat: dict[str, Any] = {
            "rank": r.get("rank"),
            "algorithm_key": r.get("algorithm_key"),
            "algorithm_id": r.get("algorithm_id"),
            "name": r.get("name"),
            "library": r.get("library"),
            "primary_metric": r.get("primary_metric"),
        }
        cv_mean = r.get("cv_mean") or {}
        cv_std = r.get("cv_std") or {}
        test = r.get("test") or {}
        for k in metric_keys:
            flat[f"cv_mean_{k}"] = cv_mean.get(k)
            flat[f"cv_std_{k}"] = cv_std.get(k)
            flat[f"test_{k}"] = test.get(k)
        writer.writerow({k: _safe_cell(v) for k, v in flat.items()})
    return buf.getvalue()
