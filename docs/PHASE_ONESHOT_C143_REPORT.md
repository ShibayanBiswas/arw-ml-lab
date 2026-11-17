# Phase oneshot-c143 — FE.WB.ADMIN_AUDIT

## Built
- `labcore/enterprise/audit.py` — deterministic demo rows (seed 42), CSV export with formula escape (SEC-11 / §46.3).
- `GET /api/v1/admin/audit` + `GET /api/v1/admin/audit/export` — owner/admin RBAC (`require_admin_role`); artefacts **`ENT.T.AUDIT_LOG`** / **`ENT.T.AUDIT_EXPORT`**.
- `AuditLogPanel` on **Admin → Audit log** — IST table + Bearer-authenticated CSV download.
- Regression: `tests/unit/test_enterprise_audit.py`, `tests/unit/test_admin_audit_api.py`, `tests/unit/test_fe_admin_audit_wb.py`; vitest `admin-api.test.ts`.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_enterprise_audit.py tests\unit\test_admin_audit_api.py tests\unit\test_fe_admin_audit_wb.py tests\unit\test_import_allowlist.py -v --tb=short
============================= test session starts =============================
collected 9 items
tests\unit\test_enterprise_audit.py ..                                   [ 22%]
tests\unit\test_admin_audit_api.py ...                                   [ 55%]
tests\unit\test_fe_admin_audit_wb.py ...                                 [ 88%]
tests\unit\test_import_allowlist.py .                                    [100%]
=================== 9 passed, 1 warning in 62.43s (0:01:02) ===================

cd frontend && pnpm exec vitest run src/lib/admin-api.test.ts
 Test Files  1 passed (1)
      Tests  1 passed (1)
```

## Notes
- Picked **enterprise audit log UI** over Locust/ZAP polish (higher product value; Admin audit was a stub).
- Distinct from oneshot-c141 **FE.WB.REPORTS_NOTEBOOK** and monitoring drift lanes (c139/c140).
- Demo `source=demo` when `DATABASE_URL` is unset; live Postgres when configured.
- No Contabo changes.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; demo rows labelled via `source`.
- [x] API `seed: 42`.
- [x] Import allowlist + vitest green.

**Ship commit:** `2c20f1d`