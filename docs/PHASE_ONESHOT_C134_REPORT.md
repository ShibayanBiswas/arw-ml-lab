# Phase oneshot-c134 — FE.WB.SUITABILITY

## Built
- `SuitabilityWorkbench` — **Run suitability** plus ten catalogue actions wired to lab-api `FS.P.*`: `FS.P.VOL`, `FS.P.PRICE`, `FS.P.BARRIERS`, `FS.P.UNIQUENESS`, `FS.P.HOLDING`, `FS.P.MIN_FFD`, `FS.P.SADF`, `FS.P.TRENDSCAN`, `FS.P.LABEL_BALANCE`, `FS.P.GRID`; Plotly via `ArtefactPanel`; DS30/DS22 sample picker.
- `runSuitabilityPlot` + `suitabilityPlotPath` + `SuitabilityCataloguePlot` in `frontend/src/lib/api.ts`.
- API gaps closed: `POST /api/v1/suitability/plots/label-balance`, `POST /api/v1/suitability/plots/grid` (seed **42** on grid numbers).
- Regression tests `tests/unit/test_fe_suitability_wb.py` + vitest `src/lib/suitability-api.test.ts`.

## Tests
```
.\.venv\Scripts\python.exe -m ruff check backend/app/routers/suitability.py
All checks passed!

.\.venv\Scripts\python.exe -m pytest tests\unit\test_fe_suitability_wb.py tests\unit\test_import_allowlist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
collected 3 items

tests\unit\test_fe_suitability_wb.py ..                                     [ 66%]
tests\unit\test_import_allowlist.py .                                        [100%]

============================== 3 passed in 3.42s ==============================

cd frontend && pnpm exec vitest run src/lib/suitability-api.test.ts
 Test Files  1 passed (1)
      Tests  1 passed (1)
```

## Notes
- Distinct from c132 **`FS.P.TRENDSCAN`** / c133 **`FE.WB.UNSUP_DR`**; c134 is finance suitability FE wiring for the full FS.P catalogue already on lab-api.
- No Contabo changes; browser calls `NEXT_PUBLIC_LAB_API_URL` only.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; plots render from API artefact JSON only.
- [x] Seed 42 on grid metadata; plot endpoints match backend stubs.
- [x] Import allowlist green; vitest route map green.

**Ship commit:** `ffa0187`