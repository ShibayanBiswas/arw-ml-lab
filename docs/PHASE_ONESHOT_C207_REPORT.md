# Phase oneshot-c207 — maintenance session DSN

## Built
- `backend/worker/maintenance.py` prefers `DATABASE_URL_SESSION` for long reaper/retention transactions.
- `tests/unit/test_maintenance_session_dsn.py`.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_maintenance_session_dsn.py tests\unit\test_maintenance.py -q --tb=line
...............                                                          [100%]
```

## Deviations
None. Contabo still blocked.
