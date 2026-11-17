# Phase oneshot-c129 — FE.WB.UNSUP_ANOM

## Built
- `UnsupervisedWorkbench` (anomaly mode) — **Run fit** plus catalogue actions wired to existing lab-api: `ANO.P.SCORE_HIST`, `ANO.P.RANKED`, `ANO.P.EMBED`; Plotly via `ArtefactPanel`; demo rows + seed **42**.
- `runUnsupervisedAnomalyPlot` + `unsupervisedAnomalyPlotPath` in `frontend/src/lib/api.ts`.
- Regression test `tests/unit/test_fe_preprocess_home.py` — `/preprocess/home` stays on `TrainWorkbench` (not `ModulePlaceholder`).

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_fe_preprocess_home.py tests\unit\test_import_allowlist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
collected 2 items

tests\unit\test_fe_preprocess_home.py .                                  [ 50%]
tests\unit\test_import_allowlist.py .                                    [100%]

============================== 2 passed in 7.21s ==============================

cd frontend && pnpm exec vitest run src/lib/unsupervised-api.test.ts
 Test Files  1 passed (1)
      Tests  1 passed (1)
```

## Notes
- Distinct from c128 **`ANO.P.PARETO`** (backend rank curve); UI deliberately omits pareto until that route is on the pinned worker image.
- No Contabo changes; browser calls `NEXT_PUBLIC_LAB_API_URL` only.
- Next gap: wire **`ANO.P.PARETO`** button after c128 lands, ANO pairwise scatter, `FS.P.SADF` / `FS.P.TRENDSCAN`, DR catalogue gaps.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; plots render from API artefact JSON only.
- [x] Seed 42 on unsupervised request body.
- [x] Import allowlist green; vitest route map green.