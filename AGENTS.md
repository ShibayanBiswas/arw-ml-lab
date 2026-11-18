# AGENTS.md — ARW ML Lab

Instructions for AI coding agents (Cursor Agent and others) working in this repository.

## What this is
A general-purpose Machine Learning Lab web app for tabular data (no NLP) for Anand Rathi Wealth. Families: Supervised (regression, classification, sequential/financial), Unsupervised (dimensionality reduction, clustering, anomaly detection) and Time Series. Full spec: `docs/ARCHITECTURE.md` v2.2 (§1–§46; evaluation suites §41–§42, Library Matrix §44, **Prediction Studio §45**, **Hardening §46** — wins over older sections; gap audit `docs/GAP_AUDIT.md`; stress-test findings `docs/STRESS_TEST.md`), flows: `docs/FLOWCHART.md` and `docs/diagrams/`. Build plan and acceptance criteria: `CURSOR_PROMPT.md`.

## How to work
1. Read `CURSOR_PROMPT.md` §00 and §000 (execution protocol: definition of done, no-stub rules, self-check, resume) and the rules in `.cursor/rules/`. If resuming, read `docs/PROGRESS.md` first.
2. For new work, plan with the strongest reasoning model when the change is large; resume from `docs/PROGRESS.md` (do not re-open finished phases).
3. Phase order (historical): 0 → 1 → 8.1 → 1A → 2 → 2A → 3 → 3A → 4 → 4A → 5B → 5 → 5A → 6 → 6A → 6B → 7 → 8.2. Contabo go-live is the open gate — see Blocked in `docs/PROGRESS.md`.
4. Run tests and acceptance criteria yourself. Keep `docs/PROGRESS.md` and `docs/FINAL_REPORT.md` current (phase report MDs were removed at wind-up).

## Layout
| Path | Purpose |
|---|---|
| `frontend/` | Next.js 16 app (Vercel, Root Directory = frontend) |
| `backend/` | FastAPI `lab-api` + Celery workers (Contabo VPS via `docker-compose.prod.yml` + Caddy, see `docs/DEPLOY_CONTABO.md`; `render.yaml` = legacy alternative) |
| `labcore/` | Pure-Python ML library (registries, CV, metrics, plots, finance, suitability, ai, insights, decisions) |
| `supabase/` | Postgres migrations, RLS, storage buckets, pgTAP tests |
| `tests/` | unit (incl. `test_predict_samples.py`), contract_tradinglab, golden, e2e, load, `db_harness/` (Docker-free migration + pgTAP runner) |
| `data/samples/` | Sample datasets, `datasets_manifest.json`, presets (seed 42), `predict/` prediction samples + feature contracts for DS1–DS33 |
| `scripts/` | `make_predict_samples.py` (regenerates `data/samples/predict`) |
| `docs/` | Architecture, flowcharts, 20 diagrams, `contracts/` (feature-contract JSON Schema), `STRESS_TEST.md`, plans, phase reports, `PROGRESS.md` |

## Commands (create them in Phase 0)
- `make dev` — local stack (`supabase start` + docker compose)
- `make test` — pytest + vitest + `supabase test db` (fallback without Docker: `python tests/db_harness/run_db_tests.py`)
- `make lint` — ruff, mypy, eslint, tsc

## Hard rules
- Never fabricate metrics, test results or plot values. Seed 42 everywhere.
- Leakage-safe pipelines; purged CV for financial labels; financial labels only after the suitability check passes.
- AI is hosted (NVIDIA API catalog via `labcore/ai`); `NVIDIA_API_KEY` only on the backend server (`/opt/arw-ml-lab/.env` on the Contabo VPS, mode 600; Render env group only on the legacy path); numbers-only fallback must always work.
- No heavy compute on Vercel. RLS on every table.
- Use only libraries pinned in `backend/requirements/*.txt` and listed in ARCHITECTURE §44; lab code is thin wrappers only (rule 70).
- Every classification run shows the full §41 evaluation suite (confusion matrix counts + row/column/all normalisations, full classification report, CV mean ± std); every regression run the §42 suite.
- Prediction Studio (§45): both modes are driven by the feature contract saved at training; never refit at prediction time; never store identifier values in contracts.
- Never stub, skip or weaken tests to go green; never mark an AC passed without running it.
- Ask the user before creating repos, connecting accounts, buying plans, setting production secrets or deploying.
- Do not commit code from the private reference repos; `refs/` is git-ignored.
