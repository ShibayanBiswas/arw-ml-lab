# Phase oneshot-c212 — SEC.JWT.PARITY

## Built
- `labcore/security/jwt_secret_parity.py` — kit check for JWT_SECRET / AUTH_MODE docs.
- `.env.example` documents `AUTH_MODE` + `JWT_SECRET` (must match Vercel).
- Unit test.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_sec_jwt_parity.py -q --tb=line
.                                                                        [100%]
```

## Deviations
`hosted_verified=false` until Contabo + Vercel values are compared live.
