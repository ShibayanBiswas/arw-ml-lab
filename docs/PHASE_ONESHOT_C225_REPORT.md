# Phase oneshot-c225 — MI.HOLDOUT.REUSE Postgres persist

## Built
- `persist_holdout_audit_row()` inserts into `public.audit_log` when given a DB executor.
- `backend/worker/tasks/train.py` best-effort persist after CV (never fails the job).
- ST-ML-04 status updated.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_mi_holdout_reuse.py -q --tb=short
...                                                                      [100%]
EXIT:0
```
