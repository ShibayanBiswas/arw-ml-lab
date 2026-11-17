# Phase oneshot-c131 — FE.WB.UNSUP_CLU

## Built
- `UnsupervisedWorkbench` (clustering mode) — **Run fit** plus six catalogue actions wired to existing lab-api: `CLU.P.ELBOW`, `CLU.P.SILHOUETTE`, `CLU.P.CH`, `CLU.P.DB`, `CLU.P.GAP`, `CLU.P.DENDROGRAM`; Plotly via `ArtefactPanel`; demo rows + seed **42**.
- `runUnsupervisedClusteringPlot` + `unsupervisedClusteringPlotPath` + `ClusteringCataloguePlot` in `frontend/src/lib/api.ts`.
- Regression tests `tests/unit/test_fe_unsup_clustering_wb.py` + vitest route map for clustering slugs.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_fe_unsup_clustering_wb.py tests\unit\test_import_allowlist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
collected 3 items

tests\unit\test_fe_unsup_clustering_wb.py ..                             [ 66%]
tests\unit\test_import_allowlist.py .                                    [100%]

============================== 3 passed in 4.04s ==============================

cd frontend && pnpm exec vitest run src/lib/unsupervised-api.test.ts
 Test Files  1 passed (1)
      Tests  2 passed (2)
```

## Notes
- Distinct from c129 **`FE.WB.UNSUP_ANOM`** (ANO catalogue) and c128 **`ANO.P.PARETO`** (backend-only); c131 is clustering-only FE wiring mirroring the anomaly workbench pattern.
- K-sweep, clustermap, reachability, k-distance routes remain API-only until a later one-shot.
- No Contabo changes; browser calls `NEXT_PUBLIC_LAB_API_URL` only.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; plots render from API artefact JSON only.
- [x] Seed 42 on unsupervised request body.
- [x] Import allowlist green; vitest route map green.