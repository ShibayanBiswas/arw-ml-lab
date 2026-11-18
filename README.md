# ARW ML Lab

General-purpose **tabular** ML lab (no NLP) for Anand Rathi Wealth: Supervised (incl. sequential/financial), Unsupervised, Time Series, EDA, explainability, uncertainty, AI Insights, and a VLM decision agent.

| Surface | URL / target | Status |
|---|---|---|
| Frontend | https://arw-ml-lab.vercel.app | Live (login 200) |
| Backend API | Contabo VPS (`docs/DEPLOY_CONTABO.md`) | **Not live** — waiting on host secrets |
| Data / Auth / Storage | Supabase | Project linked; migrate secrets still needed for Deploy |
| AI | NVIDIA API catalog (server-side only) | Key not yet on VPS |

Tip of `main`: see `docs/PROGRESS.md`. Spec: `docs/ARCHITECTURE.md` v2.3 (§1–§46).

## Start here (humans)

1. Clone the repo; Python 3.12 + `uv`, Node + `pnpm`.
2. Copy `.env.example` → `.env`. Fill Supabase + `JWT_SECRET`. Contabo / `NVIDIA_API_KEY` only when ready for the VPS.
3. Local API: `uv sync` / install from `backend/requirements/*`, then `uvicorn backend.app.main:app --reload`.
4. Frontend: `cd frontend && pnpm install && pnpm dev` (Root Directory on Vercel = `frontend`).
5. Contabo go-live: follow the **USER** section of [`docs/DEPLOY_CONTABO.md`](docs/DEPLOY_CONTABO.md), then clear the Blocked table in `docs/PROGRESS.md`.

Agents: read `AGENTS.md`, `.cursor/rules/`, and `CURSOR_PROMPT.md` §000. Resume from `docs/PROGRESS.md`.

## Layout

| Path | Purpose |
|---|---|
| `frontend/` | Next.js 16 App Router (Vercel) |
| `backend/` | FastAPI `lab-api` + Celery workers |
| `labcore/` | Pure-Python ML library (registries, CV, metrics, plots, finance, AI, predict) |
| `supabase/` | Migrations, RLS, storage, pgTAP |
| `tests/` | unit, e2e, load, security, `db_harness/`, `contract_tradinglab/` |
| `data/samples/` | Sample datasets + `predict/` contracts (seed 42) |
| `docker-compose.prod.yml`, `infra/` | Contabo compose, Caddy, deploy.sh |
| `docs/` | Architecture, deploy, stress test, phase reports, `FINAL_REPORT.md`, `PROGRESS.md` |
| `CURSOR_PROMPT.md` / `CURSOR_ONE_SHOT.md` | Build / finish reference prompts |
| `render.yaml` | **Legacy** Render Blueprint (do not delete) |

## Commands

- `make test` — pytest + vitest + DB tests (or `python tests/db_harness/run_db_tests.py`)
- `make lint` — ruff, mypy, eslint, tsc
- `make dev` — local stack when Docker/Supabase CLI are available

## Hard rules (short)

- Never fabricate metrics. Seed **42**. Leakage-safe pipelines.
- `NVIDIA_API_KEY` only on the Contabo backend `.env` — never Vercel / `NEXT_PUBLIC_*`.
- Libraries only from `backend/requirements/*.txt` + ARCHITECTURE §44 (rule 70).
- Prediction Studio (§45) never refits at serve time; feature contracts drive forms/batch.

## Honest status (wind-up)

**Code on `main` is far past a kit** — full app modules, Contabo infra files, GHCR+SSH `deploy.yml`, offline STRESS/8.2 contracts through oneshot ~c281.

**Production E2E is incomplete** until you supply Contabo SSH + GitHub Actions billing + Supabase migrate secrets + `NVIDIA_API_KEY`. See `docs/PROGRESS.md` → Blocked and `docs/FINAL_REPORT.md`.
