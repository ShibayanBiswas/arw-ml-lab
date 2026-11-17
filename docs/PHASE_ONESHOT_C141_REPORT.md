# Phase oneshot-c141 — FE.WB.REPORTS_NOTEBOOK

## Built
- `ReproductionNotebookPanel` on **Reports → Templates** — calls `POST /api/v1/reports/notebook` via `runReportsNotebook`; downloads `.ipynb`; cites artefact id **`REP.T.NOTEBOOK`** (§46.4 / ST-UX-02 reproduction export).
- `ReportsWorkbench` — mounts the panel in `templates` mode; builder behaviour unchanged.
- `frontend/src/lib/api.ts` — `reportsNotebookPath` + `runReportsNotebook` client.
- `backend/app/routers/reports.py` — notebook response includes `"id": "REP.T.NOTEBOOK"`.
- Regression: `tests/unit/test_fe_reports_notebook_wb.py`, `tests/unit/test_reports_notebook_api.py`; vitest `reports-api.test.ts`.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_fe_reports_notebook_wb.py tests\unit\test_reports_notebook_api.py tests\unit\test_import_allowlist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
collected 5 items

tests\unit\test_fe_reports_notebook_wb.py ...                            [ 60%]
tests\unit\test_reports_notebook_api.py .                                [ 80%]
tests\unit\test_import_allowlist.py .                                    [100%]

=================== 5 passed, 1 warning in 77.75s (0:01:17) ===================

cd frontend && pnpm exec vitest run src/lib/reports-api.test.ts
 Test Files  1 passed (1)
      Tests  1 passed (1)
```

## Notes
- Distinct from oneshot-c140 **PV11 batch drift** (Prediction validation PSI/KS) and c139 **`FE.WB.PREDICT_MONITOR_KS`**.
- Backend notebook builder from Phase 7 `labcore.reports.notebook` / ST-UX-02; demo FACTS are placeholders only.
- No Contabo changes.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; notebook embeds caller-supplied FACTS only.
- [x] API response `seed: 42`.
- [x] Import allowlist + vitest green.

**Ship commit:** `2b49953`