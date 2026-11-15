# ARW ML Lab — project kit

Design and build kit for the **ARW ML Lab**: a world-class, general-purpose machine-learning lab for tabular data (Supervised incl. sequential/financial, Unsupervised, Time Series) with EDA, every algorithm configurable, all CV schemes, explainability, uncertainty, financial validation (purged K-fold, CPCV, PBO, DSR, walk-forward optimisation), an AI Insights layer and a VLM decision agent. Styled like the SP Workstation modules.

**Status:** design + scaffolding only. No application code yet — Cursor builds it phase by phase.

## Start here
1. Open this folder in Cursor.
2. Open a new Agent chat and paste the message in **`CURSOR_KICKOFF.md`** (it makes the agent read `AGENTS.md`, `CURSOR_PROMPT.md` and `docs/ARCHITECTURE.md`, use the strongest reasoning model, and stop after each phase). After each phase report, send the one-line "continue" message from the same file.
3. Before Phase 6, create an NVIDIA Developer account at build.nvidia.com and an API key (free trial key for development/testing). Put it in your local `.env` and later in Render as `NVIDIA_API_KEY`. Never put it in Vercel.

## What is inside
| Path | Contents |
|---|---|
| `CURSOR_KICKOFF.md` | Short copy-paste kickoff message for Cursor Agent + the one-line "continue" message |
| `CURSOR_PROMPT.md` | Phase-by-phase build prompt (18 phases incl. 3A Prediction Studio) with acceptance criteria, execution protocol (definition of done, no-stub rules, self-check, resume) |
| `AGENTS.md` | Agent instructions |
| `.cursor/rules/*.mdc` | 11 project rules: core, stack, Python, frontend, ML integrity (incl. evaluation integrity), AI provider, testing, phase order, deployment, security, use-established-libraries |
| `docs/ARCHITECTURE.md` | Full architecture v2.2, §1–§46 (incl. §45 Prediction Studio — batch upload + custom input form, §46 Hardening — ML integrity, ops, security, UX, feature parity; §34 Deep Learning, §35 Time Series, §36 metrics/tables/plots per family, §37 financial label suitability, §38 VLM decision agent, §39 deployment, §40 hosted AI provider layer, §41 Classification Evaluation Suite, §42 Regression Evaluation Suite, §43 library gap audit, §44 Library Matrix) |
| `docs/FLOWCHART.md`, `docs/diagrams/` | 20 Mermaid diagrams (PNG + `.mmd` source) |
| `docs/STRESS_TEST.md` | Round-4 red-team audit: every finding with severity, fix and where it was fixed |
| `docs/contracts/` | Feature-contract JSON Schema used by the Prediction Studio |
| `docs/PROGRESS.md` | Build progress tracker the agent keeps current (resume point) |
| `docs/GAP_AUDIT.md` | Round-3 library gap audit: what was added, re-backed, isolated or flagged, and the dependency-resolution results |
| `backend/requirements/` | Pinned Python requirements per Render service (api, worker-light, worker-train, optional images) + `uv` lock files; see its README |
| `data/samples/` | 19 bundled sample datasets, `urls.txt`, `datasets_manifest.json/.csv`, 33 `presets/*.yaml`, and `predict/`: 35 prediction sample files for all 33 datasets (target removed, seed 42) + feature contracts |
| `scripts/make_predict_samples.py` | Regenerates the prediction samples (downloads cached; `--offline`) |
| `render.yaml` | Render Blueprint: lab-api (web), lab-worker-light and lab-worker-train (background workers), lab-beat (hourly cron), lab-kv (Key Value) |
| `frontend/vercel.json` | Vercel config for the Next.js app |
| `supabase/` | `config.toml`, 6 migrations (schema, RLS, storage buckets, helpers, Prediction Studio, hardening), seed, pgTAP RLS tests (core + prediction) |
| `tests/` | `unit/test_predict_samples.py` (38 checks) and `db_harness/` (runs the migrations and pgTAP tests on a throw-away Postgres without Docker) |
| `.github/workflows/` | `ci.yml` (lint/type/test/RLS), `deploy.yml` (migrations → Render → smoke test) |
| `.env.example` | Environment variables per platform |
| `frontend/ backend/ labcore/ infra/ vendor/` | Skeleton folders (only `backend/requirements/` is filled) |

## Deployment target
GitHub (private monorepo) → **Vercel** (frontend only) + **Render** (FastAPI API, Celery workers, Key Value) + **Supabase** (Postgres, Auth, Storage, RLS). AI calls go from Render to the **NVIDIA API catalog** (OpenAI-compatible). See `docs/ARCHITECTURE.md §39–§40`.

## Things to decide before production
- The NVIDIA API free key is a trial (dev/test). Production needs an NVIDIA AI Enterprise licence, a paid endpoint or another provider.
- Confirm with compliance that aggregate plots and metrics may be sent to the hosted AI provider (raw rows are never sent).
- TabPFN stays disabled (non-commercial weights for v2.5+).
- Re-check Render, Vercel and Supabase plan prices and limits (checked Nov 2026). Supabase must be on **Pro** with the global file size limit raised (Free caps uploads at 50 MB).
- Yahoo Finance data (NIFTY sample) is for research only; use an NSE/vendor feed in production.

The private reference repositories (sp-workstation, blackcarbon-saas, ml-for-trading) are **not** included. Clone them into `refs/` (git-ignored) with your GitHub access when Cursor needs them.
