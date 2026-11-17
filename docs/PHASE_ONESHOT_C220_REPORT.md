# Phase oneshot-c220 — SEC.LAB_AUTH.BYPASS

## Built
- `labcore/security/lab_auth_bypass_guard.py` — `.env.example` defaults `LAB_AUTH_BYPASS=false`; `DEPLOY.md` forbids it in production; no `NEXT_PUBLIC_LAB_AUTH_BYPASS=true` in env templates.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_sec_lab_auth_bypass.py tests\unit\test_sec_auth_bypass.py -q --tb=line
..                                                                       [100%]
EXIT:0
```
