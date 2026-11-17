# Phase oneshot-c218 — SEC.AUTH.BYPASS prod pin

## Built
- `labcore/security/auth_bypass_guard.py` — asserts `.env.example` defaults `AUTH_TEST_BYPASS=false`, `DEPLOY_CONTABO.md` lists `AUTH_TEST_BYPASS=false`, and `docker-compose.prod.yml` forces `AUTH_TEST_BYPASS: "false"` on lab-api, worker-light, worker-train, lab-beat.
- Compose environment override so a mistaken server `.env` cannot enable bypass in Contabo prod.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_sec_auth_bypass.py -q --tb=line
.                                                                        [100%]
EXIT:0
```

## Contabo / Actions
Still blocked — no `CONTABO_HOST`; Actions billing fails (~2–4s). Hosted prove deferred.
