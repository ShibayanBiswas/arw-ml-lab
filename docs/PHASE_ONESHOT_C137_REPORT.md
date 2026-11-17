# Phase oneshot-c137 — FE.WB.UNSUP_ANOM_PARETO_PAIRWISE

## Built
- `UnsupervisedWorkbench` (anomaly mode) — added catalogue actions **`ANO.P.PARETO`** and **`ANO.P.PAIRWISE`** alongside existing score-hist / ranked / embed (c129); calls existing lab-api routes; Plotly via `ArtefactPanel`; demo rows + seed **42**.
- `AnomalyCataloguePlot` extended with `"pareto"` | `"pairwise"` in `frontend/src/lib/api.ts`; vitest route map updated.
- Regression test `tests/unit/test_fe_unsup_anomaly_wb.py` — asserts all five ANO.P artefact ids in the workbench and API type.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_fe_unsup_anomaly_wb.py tests\unit\test_import_allowlist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
collected 3 items

tests\unit\test_fe_unsup_anomaly_wb.py ..                                [ 66%]
tests\unit\test_import_allowlist.py .                                    [100%]

============================== 3 passed in 4.31s ==============================

cd frontend && pnpm exec vitest run src/lib/unsupervised-api.test.ts
 Test Files  1 passed (1)
      Tests  3 passed (3)
```

## Notes
- No remaining module nav routes hit `ModulePlaceholder` (fallback only); this step closes the PROGRESS gap: wire **`ANO.P.PARETO`** in anomaly WB (pairwise shipped in same pass after c135 backend).
- Pairwise uses API default `top_features=4` on the server (`UnsupBody`).
- Next gap: **`DR.P.SHEPARD`** in DR WB; remaining **`CLU.P.*`** (k-sweep, clustermap, reachability, k-distance) in FE.
- No Contabo changes.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; plots render from API artefact JSON only.
- [x] Seed 42 on unsupervised request body.
- [x] Import allowlist green; vitest route map green.

**Ship commit:** (recorded after commit)