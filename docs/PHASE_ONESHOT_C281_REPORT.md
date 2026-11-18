# Phase oneshot-c281 — OPS.COST.GUARDS + Admin quotas

## Built
- `labcore/ops/cost_guards.py`: Contabo concurrency / CPU-hours / storage / AI daily limits.
- `GET /api/v1/admin/quotas` + Admin FE quotas panel (`OPS.COST.GUARDS`).
- Workspaces mode copy for hosted membership.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests/unit/test_ops_cost_guards.py -q --tb=short
....                                                                     [100%]
```

## Contabo
Still blocked — `CONTABO_HOST` missing; Actions billing still kills CI in ~2s.
