# Phase oneshot-c151 — SEC.CORS.BEARER

## Built
- `labcore/security/api_auth_policy.py` — **SEC-07** policy constants + `reject_cookie_without_bearer`; artefact **`SEC.CORS.BEARER`**, seed **42**.
- `backend/app/main.py` — CORS middleware wired from policy module; HTTP middleware returns 401 when `Cookie` is sent without `Authorization: Bearer` (exempt OPTIONS, `/healthz`, docs).
- `docs/STRESS_TEST.md` — **ST-SEC-07** → `fixed + tested`.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_sec07_cors_bearer.py tests\unit\test_import_allowlist.py -v --tb=short
============================== 6 passed in 70.30s ==============================
```

## Notes
- Closes **ST-SEC-07** (Low) offline — the only remaining STRESS item after **ST-OPS-10** (CI CLI pin, typical oneshot-c150 lane).
- Distinct from oneshot-c150 **ST-OPS-10** (Supabase CLI version contract in workflows).
- Distinct from oneshot-c149 **OPS.EGRESS.ALLOWLIST** (ST-OPS-08).
- Seed **42** on manifest; no Contabo / NVIDIA / live deploy.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated CORS origins; policy tested via TestClient + pure helpers.
- [x] Import allowlist green.
- [x] Rule 70: stdlib + existing FastAPI stack only in new module.

**Ship commit:** `6f537ba`