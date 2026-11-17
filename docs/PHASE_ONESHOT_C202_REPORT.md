# Phase oneshot-c202 — OPS.POOLER.URLS

## Built
- `Settings.database_url_session` + `resolved_optuna_storage_url()`.
- Tune worker falls back to session pooler for Optuna storage.
- `labcore/ops/pooler_urls.py` kit contract.
- Tests.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ops_pooler_urls.py tests\unit\test_tune_optuna_storage_wiring.py -v --tb=short
============================== 5 passed in 1.74s ==============================
```

## Deviations
None. Contabo still blocked.

## TODOs
Confirm hosted Supabase pooler ports 6543 (tx) / 5432 (session) in server `.env`.
