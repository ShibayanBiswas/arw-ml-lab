# Phase oneshot-c142 — FE.WB.REPORTS_EXECUTIVE

## Built
- `ExecutiveSummaryPanel` on **Reports → Templates** — calls `POST /api/v1/reports/executive` via `runReportsExecutive`; downloads HTML (+ optional PDF when WeasyPrint/Pango is present); cites artefact id **`REP.T.EXECUTIVE`** (ARCHITECTURE §25).
- `labcore/reports/executive.py` — FACTS-only HTML executive summary; optional PDF via WeasyPrint.
- `frontend/src/lib/api.ts` — `reportsExecutivePath` + `runReportsExecutive`.
- `backend/app/routers/reports.py` — executive route; build response now tags `REP.T.BUILDER`.
- Regression: `tests/unit/test_executive_summary.py`, `tests/unit/test_reports_executive_api.py`, `tests/unit/test_fe_reports_executive_wb.py`; vitest `reports-api.test.ts`.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_executive_summary.py tests\unit\test_reports_executive_api.py tests\unit\test_fe_reports_executive_wb.py tests\unit\test_import_allowlist.py -v --tb=short
=================== 6 passed, 1 warning in 76.73s (0:01:16) ===================

cd frontend && pnpm exec vitest run src/lib/reports-api.test.ts
 Test Files  1 passed (1)
      Tests  2 passed (2)
```

## Notes
- Distinct from oneshot-c141 **`REP.T.NOTEBOOK`**; pairs with the stub JSON-only builder on Reports → Builder.
- PDF path is best-effort on dev Windows (WeasyPrint often absent); Docker worker image has Pango.
- No Contabo changes.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; HTML lists caller-supplied FACTS only.
- [x] API response `seed: 42`.
- [x] Import allowlist + vitest green.

**Ship commits:** `33a7596` (feature), `073ef08` (vitest route)