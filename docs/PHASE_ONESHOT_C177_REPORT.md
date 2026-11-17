# Phase oneshot-c177 — REP.T.LEADERBOARD

## Built
- `labcore/train/export.py` — shared flatten helpers; **`leaderboard_to_xlsx_bytes`** (openpyxl + SEC-04 escape).
- `labcore/reports/leaderboard_export.py` — offline artefact **`REP.T.LEADERBOARD`** for ST-UX-02 (CSV + XLSX kit contract).
- `backend/app/routers/experiments.py` — `GET /api/v1/experiments/{id}/leaderboard.xlsx`.
- `tests/unit/test_rep_t_leaderboard_export.py` — manifest, metric columns, formula escape in XLSX XML.
- `docs/STRESS_TEST.md` — **ST-UX-02** offline row notes **REP.T.LEADERBOARD**.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_rep_t_leaderboard_export.py tests\unit\test_sec04_formula_escape.py tests\unit\test_import_allowlist.py -v --tb=short
============================= 16 passed in 38.71s =============================
```

## Notes
- Distinct from oneshot-c176 reproduction-bundle lane (ST-UX-02 remainder); c177 is leaderboard CSV/XLSX export only offline.
- Reuses existing `leaderboard_to_csv` path; lazy `openpyxl` import matches `template_xlsx_bytes`.
- Seed **42**; no Contabo.

## Self-check (CURSOR_PROMPT §000)
- [x] Demo rows: CSV and XLSX escape `=` / `+` triggers per SEC-04.
- [x] XLSX flattens `cv_mean_*` / `cv_std_*` / `test_*` metric columns.
- [x] Import allowlist green.
- [x] Rule 70: openpyxl write + `escape_formula_export_cell` only; no custom XLSX/XML.

**Ship commit:** `6f33282`