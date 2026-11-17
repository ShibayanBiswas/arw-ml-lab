"""Audit log listing and CSV export (SEC-11 / ARCHITECTURE §25 enterprise)."""

from __future__ import annotations

import csv
import io
import json
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from labcore.security.formula_escape import escape_formula_export_cell

_AUDIT_DEMO_ACTIONS: tuple[tuple[str, str, str], ...] = (
    ("decision.approve", "decision", "VD3"),
    ("prediction.batch", "prediction_job", "PJ-demo"),
    ("report.export", "report", "REP.T.NOTEBOOK"),
    ("test.evaluation", "run", "run-holdout"),
    ("ai.insight.generate", "artefact", "INS-042"),
    ("dataset.upload", "dataset_version", "DS1-v1"),
)

CSV_COLUMNS: tuple[str, ...] = (
    "id",
    "created_at",
    "user_id",
    "action",
    "entity",
    "entity_id",
    "detail_json",
)


def _parse_uuid(value: str | UUID) -> UUID:
    if isinstance(value, UUID):
        return value
    return UUID(str(value))


def demo_audit_rows(
    workspace_id: str,
    *,
    seed: int = 42,
    count: int = 12,
) -> list[dict[str, Any]]:
    """Deterministic placeholder rows when Postgres is unavailable (offline Phase 7)."""
    ws = _parse_uuid(workspace_id)
    rng = __import__("random").Random(seed)
    base = datetime(2026, 11, 17, 6, 30, tzinfo=UTC)
    rows: list[dict[str, Any]] = []
    for i in range(min(count, len(_AUDIT_DEMO_ACTIONS) * 2)):
        action, entity, entity_id = _AUDIT_DEMO_ACTIONS[i % len(_AUDIT_DEMO_ACTIONS)]
        ts = base - timedelta(minutes=rng.randint(5, 600) + i * 3)
        rows.append(
            normalize_audit_row(
                {
                    "id": 10_000 + i,
                    "workspace_id": str(ws),
                    "user_id": "00000000-0000-0000-0000-000000000099",
                    "action": action,
                    "entity": entity,
                    "entity_id": f"{entity_id}-{i}",
                    "detail": {"seed": seed, "split": "oof", "prompt_hash": f"ph-{rng.randint(1000, 9999)}"},
                    "created_at": ts.isoformat(),
                }
            )
        )
    rows.sort(key=lambda r: r["created_at"], reverse=True)
    return rows


def normalize_audit_row(raw: dict[str, Any]) -> dict[str, Any]:
    """Shape a DB or demo row for API/FE (no secret fields in detail)."""
    detail = raw.get("detail") or {}
    if not isinstance(detail, dict):
        detail = {"value": detail}
    safe_detail = {k: v for k, v in detail.items() if k.lower() not in {"api_key", "token", "secret", "password"}}
    created = raw.get("created_at")
    if isinstance(created, datetime):
        created_s = created.astimezone(UTC).isoformat()
    else:
        created_s = str(created or "")
    return {
        "id": int(raw["id"]),
        "workspace_id": str(raw.get("workspace_id") or ""),
        "user_id": str(raw.get("user_id") or ""),
        "action": str(raw.get("action") or ""),
        "entity": raw.get("entity"),
        "entity_id": raw.get("entity_id"),
        "detail": safe_detail,
        "created_at": created_s,
    }


def audit_rows_to_csv(rows: list[dict[str, Any]]) -> str:
    """SEC-11 admin audit export — formula-safe CSV (SEC-04 on every column)."""
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(CSV_COLUMNS)
    for row in rows:
        detail_json = json.dumps(row.get("detail") or {}, sort_keys=True)
        writer.writerow(
            [
                escape_formula_export_cell(row.get("id")),
                escape_formula_export_cell(row.get("created_at")),
                escape_formula_export_cell(row.get("user_id")),
                escape_formula_export_cell(row.get("action")),
                escape_formula_export_cell(row.get("entity") or ""),
                escape_formula_export_cell(row.get("entity_id") or ""),
                escape_formula_export_cell(detail_json),
            ]
        )
    return buf.getvalue()