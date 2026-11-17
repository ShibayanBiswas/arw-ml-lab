# Phase oneshot-c138 — FE.WB.UNSUP_CLU_KSWEEP_MAP_REACH_KDIST

## Built
- `UnsupervisedWorkbench` (clustering mode) — four remaining catalogue actions wired to existing lab-api: `CLU.P.K_SWEEP`, `CLU.P.CLUSTERMAP`, `CLU.P.REACHABILITY`, `CLU.P.K_DISTANCE`; Plotly via `ArtefactPanel`; demo rows + seed **42**.
- `ClusteringCataloguePlot` extended with `k-sweep`, `clustermap`, `reachability`, `k-distance` in `frontend/src/lib/api.ts`; vitest route map updated.
- `tests/unit/test_fe_unsup_clustering_wb.py` — asserts full **CLU.P.*** catalogue (10 artefacts) in workbench source.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_fe_unsup_clustering_wb.py tests\unit\test_import_allowlist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
collected 3 items

tests\unit\test_fe_unsup_clustering_wb.py ..                             [ 66%]
tests\unit\test_import_allowlist.py .                                    [100%]

============================== 3 passed in 5.41s ==============================

cd frontend && pnpm exec vitest run src/lib/unsupervised-api.test.ts
 Test Files  1 passed (1)
      Tests  3 passed (3)
```

## Notes
- Backends from oneshot-c103/c122/c123/c124; c131 wired the first six CLU plots only.
- Clustering FE catalogue is now complete vs lab-api `POST /api/v1/unsupervised/clustering/*`.
- No Contabo changes.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; plots from API artefact JSON only.
- [x] Seed 42 on unsupervised request body.
- [x] Import allowlist + vitest green.

**Ship commit:** `0f4a100`