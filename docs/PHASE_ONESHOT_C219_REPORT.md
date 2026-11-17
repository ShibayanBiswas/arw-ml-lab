# Phase oneshot-c219 — FE.NAV.COVERAGE

## Built
- `labcore/ux/nav_coverage.py` — parses `frontend/src/lib/modules.ts` nav leaves and `page.tsx` route branches; fails if any leaf would fall through to `<ModulePlaceholder />`.
- Confirms catch-alls for `eda` / `learn` and explicit routes for data/preprocess/supervised/unsupervised/timeseries/explain/predict/experiments/reports/admin.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_fe_nav_coverage.py -q --tb=short
.                                                                        [100%]
EXIT:0
```

## Contabo / Actions
Still blocked (no CONTABO_HOST; Actions billing).
