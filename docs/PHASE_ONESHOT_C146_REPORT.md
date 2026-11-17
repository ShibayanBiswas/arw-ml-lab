# Phase oneshot-c146 — REP.T.FORMULAS

## Built
- `labcore/reports/formulas.py` — curated CLE.M.* / REE.M.* LaTeX catalogue (12 entries), `build_formula_sheet`, KaTeX HTML export artefact **`REP.T.FORMULAS`**, seed **42**.
- `POST /api/v1/reports/formulas` — optional `families` filter (`classification` | `regression`).
- `FormulaSheetPanel` on **Reports → Templates** — preview via KaTeX + HTML download; `runReportsFormulas` in `api.ts`.
- Regression: `test_formula_sheet.py`, `test_reports_formulas_api.py`, `test_fe_reports_formulas_wb.py`.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_formula_sheet.py tests\unit\test_reports_formulas_api.py tests\unit\test_fe_reports_formulas_wb.py tests\unit\test_import_allowlist.py -v --tb=short
=================== 7 passed, 1 warning in 61.63s (0:01:01) ===================
```

## Notes
- Follows oneshot-c144 deferral of REP.T.FORMULAS; pairs with **REP.T.EXECUTIVE** and **REP.T.NOTEBOOK** on Templates.
- Formula sheet is reference-only (no fabricated metric values). HTML uses KaTeX 0.19.1 CDN to match frontend.
- No Contabo changes.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; entries are static LaTeX reference.
- [x] Seed 42 on API response.
- [x] Import allowlist green.

**Ship commit:** `8e379aa`