# Phase oneshot-c222 — OPS.HEALTHCHECK.PING

## Built
- `backend/worker/maintenance.py` `ping_healthcheck()` — GET `HEALTHCHECK_PING_URL` after hourly tasks (DEPLOY_CONTABO §11); unset → no-op.
- `.env.example` documents the optional URL.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_maintenance.py tests\unit\test_sec_lab_auth_bypass.py tests\unit\test_ops_backup_script.py -q --tb=short
..................                                                       [100%]
EXIT:0
```
