# Phase oneshot-c137 — FE.WB.UNSUP_DR_SHEPARD

## Built
- `UnsupervisedWorkbench` (DR mode) — catalogue action **`DR.P.SHEPARD`** wired to `POST /api/v1/unsupervised/dr/shepard`; Plotly via `ArtefactPanel`; demo rows + seed **42**.
- `DrCataloguePlot` extended with `"shepard"` in `frontend/src/lib/api.ts`; vitest route map updated.
- `tests/unit/test_fe_unsup_dr_wb.py` — asserts **`DR.P.SHEPARD`** in workbench source.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_fe_unsup_dr_wb.py tests\unit\test_import_allowlist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
collected 3 items

tests\unit\test_fe_unsup_dr_wb.py ..                                     [ 66%]
tests\unit\test_import_allowlist.py .                                    [100%]

============================== 3 passed in 3.43s ==============================

cd frontend && pnpm exec vitest run src/lib/unsupervised-api.test.ts
 Test Files  1 passed (1)
      Tests  3 passed (3)
```

## Notes
- Backend from oneshot-c34; c133 DR WB omitted Shepard until this step.
- ModulePlaceholder: no nav routes use it (fallback only). c136 (`9553dbc`) shipped anomaly Pareto/pairwise FE.
- Next gap: **CLU.P.*** k-sweep, clustermap, reachability, k-distance in clustering FE.
- No Contabo changes.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; plots from API artefact JSON only.
- [x] Seed 42 on unsupervised request body.
- [x] Import allowlist + vitest green.

**Ship commit:** _(after commit)_