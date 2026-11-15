# Phase 0 — Foundations plan

Approved plan for Phase 0. Source: Cursor plan `phase_0_foundations_2e4f178c`.

## Decisions

- **SP design source:** Clone `ShibayanBiswas/sp-workstation` into `refs/sp-workstation` (git-ignored). Port tokens/shell/`modules.ts` from that tree. If clone fails, implement from `CURSOR_PROMPT.md` §1.1 + `docs/ARCHITECTURE.md` §5 and record in `docs/DECISIONS.md`.
- **Local verification:** Full `Makefile` + `infra/docker-compose.yml` + `supabase start`. Prefer full AC when Docker works; fall back to `python tests/db_harness/run_db_tests.py` without weakening tests.
- **Out of scope:** GitHub remote/create/push, Vercel/Render/Supabase hosted, paid plans, production secrets, TradingLab submodule (Phase 5).

## Starting point

Kit already has: spec/docs, 6 Supabase migrations + 2 pgTAP tests, `backend/requirements/*` + locks, `render.yaml`, `.env.example`, CI/deploy workflows, `data/samples/`, `tests/unit/test_predict_samples.py`, `tests/db_harness/`. Empty: `frontend/` (only `vercel.json`), `backend/` (no app/Dockerfile), `labcore/`, `infra/`, `vendor/`. No git repo yet.

## Architecture

Browser → Next.js BFF + Auth → Supabase local. Browser SSE → lab-api directly. lab-api ↔ Redis ↔ Celery worker ↔ Supabase.

## Workstreams

### A. Repo + tooling

- `git init`; `.gitignore` covers `.env`, `refs/`, caches
- Root `pyproject.toml`: Python 3.12, packages `labcore` + `backend`, ruff/mypy/pytest
- `Makefile`: `make dev`, `make test`, `make lint`
- `infra/docker-compose.yml`: frontend, lab-api, worker, redis
- `backend/Dockerfile` matching `render.yaml`
- Pin Supabase CLI in CI (ST-OPS-10)
- Create `docs/DECISIONS.md`, `docs/TODO.md`

### B. Database

- Use kit's six migrations as-is (30 tables)
- Verify via `supabase db reset` + `supabase test db` or db_harness

### C. Backend

- `/healthz`, CORS, OTel, slowapi
- JWT via Supabase JWKS; Bearer-only; RBAC (viewer denied on POST)
- `ParamSpec`/`AlgorithmSpec`; empty-but-typed `GET /catalog/...`
- Celery all queues; SSE `GET /jobs/{id}/events`; dummy progress job
- Import-allow-list CI; re-run `uv pip compile` for 3.12

### D. Frontend

- Next.js 16 + React 19 + TS 5 + Tailwind 4 + pnpm
- SP shell tokens, 13 modules, light/dark, collapsible sidebar
- Supabase Auth OTP; `JobProgress` SSE; Vitest shell snapshot

### E. Acceptance criteria

1. `make lint` + `make test` green
2. Migrations + pgTAP green
3. OTP login + 13 modules + collapse + theme
4. Dummy Celery → JobProgress SSE
5. `uv pip compile` + import-allow-list pass
6. §000 self-verification checklist in report

### F. Close-out

`docs/PHASE_0_REPORT.md`, update `docs/PROGRESS.md`, commit `phase 0: foundations`, STOP.

## Explicitly not in Phase 0

Upload/EDA, Prediction Studio UI, ML algorithms, TradingLab, hosted deploy, NVIDIA live calls in CI.
