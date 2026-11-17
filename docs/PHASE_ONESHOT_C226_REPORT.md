# Phase oneshot-c226 — MI.HOLDOUT.REUSE workspace_id

## Built
- `TrainConfig.workspace_id` (default `offline`) flows into hold-out audit rows.
- Worker train task passes `body["workspace_id"]` so Postgres `audit_log.workspace_id` can be a real UUID when the API supplies it.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_mi_holdout_reuse.py -q --tb=line
...                                                                      [100%]
EXIT:0
```
