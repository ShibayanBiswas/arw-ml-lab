# Phase 0 report — Foundations

Date: 2026-11-15 (IST). Seed: 42.

## What was built

- Local git repo (`git init`); tooling: `Makefile`, `pyproject.toml`, `infra/docker-compose.yml`, `backend/Dockerfile`
- `labcore` package with `ParamSpec` / `AlgorithmSpec` and empty typed `GET /catalog`
- FastAPI `lab-api`: `/healthz`, JWT/JWKS auth helpers, RBAC (viewer denied on POST), jobs + SSE, demo Celery task
- Celery app with all documented queues (+ `q.demo` for Phase 0 AC)
- Next.js 16 frontend: SP Workstation tokens/shell ported from `refs/sp-workstation` (git-ignored clone), 13 sidebar entries (Home Terminal + 12 modules with nested sub-pages), light/dark, collapsible sidebar, OTP login page, `JobProgress`
- Import-allow-list test; CI Supabase CLI pinned to `3.1.0` (ST-OPS-10)
- `docs/DECISIONS.md`, `docs/PROGRESS.md`, `docs/plans/PHASE_0_PLAN.md`
- `PyJWT` declared in `backend/requirements/api.txt`; `api.lock.txt` recompiled

## Acceptance criteria

| AC | Result | Evidence |
|---|---|---|
| `make test` / unit + vitest | **PASS** | pytest `47 passed`; vitest `4 passed` |
| Migrations + pgTAP RLS | **PASS** (db_harness) | 6/6 migrations ok; 14 assertion lines ok (see below) |
| `supabase start` + compose healthy | **PARTIAL** | Docker Redis healthy; Supabase CLI not installed on this Windows host — used `tests/db_harness/run_db_tests.py` instead (allowed fallback) |
| Login OTP + 13 modules + collapse + theme | **PASS** (code + tests) | Login page + Inbucket instructions; `MODULE_COUNT === 13`; shell token snapshot; collapse key `arw-sidebar-collapsed` |
| Dummy Celery → SSE / JobProgress | **PASS** | Unit SSE test + smoke: job `202` → status `done` progress `1.0` |
| `uv pip compile` + import allow-list | **PASS** | `api.lock.txt` recompiled; import allow-list green |
| Lint / type / build | **PASS** | ruff + mypy labcore; eslint + `tsc`; `pnpm build` green |

### Real command output (summaries)

**pytest**
```
...............................................                          [100%]
47 passed
```

**vitest**
```
Test Files  2 passed (2)
Tests  4 passed (4)
```

**db_harness**
```
ok   20261114000000_core_schema.sql
ok   20261114000100_rls_policies.sql
ok   20261114000200_storage_buckets.sql
ok   20261114000300_helpers.sql
ok   20261115000000_prediction_studio.sql
ok   20261115000100_hardening.sql
== prediction_rls_test.sql
 ok - member of A reads A results (got 1)
 ok - member of A reads the contract (got 1)
 ok - analyst can create a prediction job
 ok - users cannot write prediction results (worker only) (42501 ...)
 ok - users cannot fabricate metrics (42501 ...)
 ok - malformed storage path is denied, not a cast error (42501 ...)
 ok - analyst can upload a prediction input to own workspace
 ok - users cannot change prediction job status (worker only) (got 0)
 ok - member of B cannot see A prediction jobs (got 0)
 ok - member of B cannot see A results (got 0)
== rls_test.sql
 ok - user A sees only workspace A datasets (got 1)
 ok - user A sees ds-a (got ds-a)
 ok - user B sees only workspace B datasets (got 1)
 ok - viewer cannot insert (42501 ...)
```

**API smoke**
```
health {'status': 'ok', 'seed': 42, 'service': 'api', 'ai_enabled': False}
job 202 {'job_id': '177ccff6-de11-48f0-b929-4650517c5098'}
status {... 'status': 'done', 'progress': 1.0, 'result': {'seed': 42, 'ok': True}}
```

**frontend build**
```
Route (app)
┌ ƒ /
├ ○ /login
├ ƒ /[module]
├ ƒ /[module]/[page]
└ ƒ /auth/callback
```

## Self-verification checklist (§000)

- [x] `make lint` / equivalent green (ruff, mypy, eslint, tsc) and tests green
- [x] DB migrations + RLS via `python tests/db_harness/run_db_tests.py` (Docker-free; Supabase CLI not on PATH)
- [x] `rg`/search for TODO|FIXME|NotImplementedError|pass # stub in labcore/backend/frontend/src — no hits
- [x] Endpoints added match §6.2 paths used in Phase 0 (`/healthz`, `/api/v1/auth/me`, `/api/v1/catalog/*`, `/api/v1/jobs/*`); tables from kit migrations unchanged
- [x] No secrets in diff; `NVIDIA_API_KEY` not in frontend
- [x] Seed 42 on healthz and demo job result
- [x] Screens have empty/loading/error via `ModulePlaceholder`; login + shell keyboard-labelled controls

## Deviations

1. **Supabase CLI** not installed locally → verified RLS with db_harness (space-safe psql quoting added for Windows OneDrive paths).
2. **Compose full stack** not run end-to-end in this session (Redis verified; API smoke via TestClient + eager Celery). Images/Dockerfile are present for `make dev`.
3. **`worker-train.lock.txt`**: kit lock retained; `api.lock.txt` recompiled after declaring `PyJWT`. Full worker-train re-resolve deferred if network/time constrained — no pin bumps beyond PyJWT.
4. **Next.js `cacheComponents`**: left off for Phase 0 because the lab layout reads cookies.

## Open TODOs

See `docs/PROGRESS.md` — install Supabase CLI for `supabase start` / `supabase test db` on this machine; optional Playwright axe smoke later.

## Next phase

**Phase 1 — Data + EDA + Education + rule-based insights** (upload, type inference, sample loader DS1–DS33, EDA tables/plots, ExplainCard, rule insights).

STOP — waiting for "continue".
