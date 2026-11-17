"""labcore.enterprise.audit — deterministic demo rows and CSV export."""

from __future__ import annotations

from labcore.enterprise.audit import audit_rows_to_csv, demo_audit_rows

WS = "00000000-0000-0000-0000-000000000010"


def test_demo_audit_rows_seed_42_stable() -> None:
    a = demo_audit_rows(WS, seed=42, count=6)
    b = demo_audit_rows(WS, seed=42, count=6)
    assert a == b
    assert all(r["detail"].get("seed") == 42 for r in a)


def test_audit_csv_escapes_formula_cells() -> None:
    rows = demo_audit_rows(WS, seed=42, count=1)
    rows[0]["action"] = "=1+1"
    rows[0]["detail"] = {"note": "=1+1"}
    csv_text = audit_rows_to_csv(rows)
    assert "'=1+1" in csv_text
    assert csv_text.splitlines()[0] == "id,created_at,user_id,action,entity,entity_id,detail_json"