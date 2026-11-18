# Phase oneshot-c276 — Admin workers panel + Locust auth opt-in + in-lab finance oracles

## Built
- `labcore/ops/queue_stats.py` + `GET /api/v1/admin/workers` (OPS.ADMIN.WORKERS).
- Admin FE `workers` mode fetches queue depths (not raw healthz).
- Locust: opt-in `LabApiAuthBypassUser` behind `LAB_LOAD_AUTH_BYPASS` (public scenario stays secrets-free).
- `tests/contract_tradinglab/test_inlab_finance_oracles.py`: purged / CPCV / PBO offline without TradingLab submodule.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests/unit/test_ops_admin_workers.py tests/unit/test_load_locust_api.py tests/contract_tradinglab/ -q --tb=short
# (admin + locust + oracles green; TradingLab parity still skipped)
```

## Contabo
Still blocked — `CONTABO_HOST` missing; Actions billing still kills CI in ~2s.
