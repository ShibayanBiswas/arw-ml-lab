# Phase oneshot-c133 — FE.WB.UNSUP_DR

## Built
- `UnsupervisedWorkbench` (DR mode) — **Run fit** plus five catalogue actions wired to existing lab-api: `DR.P.SCREE`, `DR.P.CUMVAR`, `DR.P.BIPLOT`, `DR.P.LOADINGS`, `DR.P.CORR_CIRCLE`; Plotly via `ArtefactPanel`; demo rows + seed **42**.
- `runUnsupervisedDrPlot` + `unsupervisedDrPlotPath` + `DrCataloguePlot` in `frontend/src/lib/api.ts`.
- Regression tests `tests/unit/test_fe_unsup_dr_wb.py` + vitest route map for DR slugs.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_fe_unsup_dr_wb.py tests\unit\test_import_allowlist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
collected 3 items

tests\unit\test_fe_unsup_dr_wb.py ..                                     [ 66%]
tests\unit\test_import_allowlist.py .                                    [100%]

============================== 3 passed in 4.47s ==============================

cd frontend && pnpm exec vitest run src/lib/unsupervised-api.test.ts
 Test Files  1 passed (1)
      Tests  3 passed (3)
```

## Notes
- Distinct from c131 **`FE.WB.UNSUP_CLU`** and c129 **`FE.WB.UNSUP_ANOM`**; c133 is DR-only FE wiring mirroring the clustering/anomaly workbench pattern.
- `DR.P.SHEPARD` remains API-only until a later one-shot.
- No Contabo changes; browser calls `NEXT_PUBLIC_LAB_API_URL` only.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; plots render from API artefact JSON only.
- [x] Seed 42 on unsupervised request body.
- [x] Import allowlist green; vitest route map green.

**Ship commit:** `b09a19e`