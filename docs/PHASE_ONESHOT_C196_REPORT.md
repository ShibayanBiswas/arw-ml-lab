# Phase oneshot-c196 — MI.HOLDOUT.REUSE FE badge

## Built
- `labcore/integrity/holdout_reuse_ui.py` — badge helper + contract.
- TrainWorkbench surfaces `result.holdout_reuse` (`data-artefact="MI.HOLDOUT.REUSE"`).
- `tests/unit/test_holdout_reuse_ui.py`.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_holdout_reuse_ui.py -v --tb=line
============================== 1 passed in 6.59s ==============================
```

## Deviations
None. Contabo/Actions still blocked.

## TODOs
Persist holdout audit rows to Postgres `audit_log` on hosted workers.
