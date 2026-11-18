# ARW ML Lab — Final wind-up report

**Date:** 18 Nov 2026 (IST)  
**Tip before prune commit:** `7b81299` (oneshot-c281)  
**Repo:** https://github.com/ShibayanBiswas/arw-ml-lab (`main`)

## Verdict

**Codebase: largely complete for offline / Contabo-ready kit.**  
**Production system: NOT end-to-end green.** Contabo API, Deploy, and hosted DS1 EDA cannot be proven until secrets + Actions billing are fixed.

| Layer | Result | Evidence |
|---|---|---|
| Repo `main` | Up to date with Contabo infra + app | Tip `7b81299`; prune commit follows |
| Local API (TestClient) | Pass | `/healthz` 200 seed **42**; `/api/v1/catalog/algorithms` **83**; samples 200 |
| Local unit/e2e slice | Pass | import allowlist, cost guards, GPU guard, soft-limit contract, nav coverage, feature-contract UQ, hosted FE + journey HTTP |
| Frontend tsc | Pass | `pnpm exec tsc --noEmit` clean |
| Vercel frontend | Live | `https://arw-ml-lab.vercel.app/login` → **200**; `/` → **307** |
| Vercel → Contabo API | Missing | `NEXT_PUBLIC_LAB_API_URL` is localhost/placeholder; no Contabo hostname |
| Local uvicorn :8000 | Down | Not running in this session (TestClient covers API smoke) |
| Contabo `/healthz` | Not available | `CONTABO_HOST` missing |
| GitHub Actions CI | Fail | Billing; jobs die in ~2s with empty steps |
| Deploy workflow | Skipped | Needs CI green + Contabo secrets |
| DS1 EDA → Storage → SSE | Not proven hosted | Requires live Contabo + Supabase service role |

## What shipped (summary)

- Full App Router workbenches (data, EDA, train, unsupervised, TS, explain, predict, experiments, reports, admin, learn).
- Contabo v2.3: `docker-compose.prod.yml`, Caddy, `deploy.sh`, bootstrap script, GHCR+SSH `deploy.yml`, ADR-0017.
- Prediction Studio §45, evaluation suites, STRESS offline contracts, SoftTimeLimit mid-run, cancel flags, OTLP/JSON logs, admin workers/quotas, Contabo DL presets, feature-contract UQ schema.
- Docs wind-up: removed ~252 oneshot phase reports + one-time Cursor prompts + draft plans.

## Blocked on Shibayan (exact)

1. https://github.com/settings/billing — Actions payment / spend limit.  
2. Local `.env`: `CONTABO_HOST`, `CONTABO_SSH_KEY_PATH`, `ACME_EMAIL`, Supabase service/S3/DB URLs, `NVIDIA_API_KEY`.  
3. `gh secret set` (stdin, `--env production`): `CONTABO_HOST`, `CONTABO_KNOWN_HOSTS`, `SUPABASE_ACCESS_TOKEN`, `SUPABASE_DB_PASSWORD`.  
4. After hostname: `gh variable set LAB_API_URL` + Vercel `NEXT_PUBLIC_LAB_API_URL` + redeploy.  

Then agent can: SSH bootstrap → server `.env` → Deploy green → curl `/healthz` → browser DS1 EDA → rollback drill → final Contabo prove.

## Docs after prune

Canonical: `README.md`, `AGENTS.md`, `CURSOR_PROMPT.md`, `CURSOR_ONE_SHOT.md`, `docs/ARCHITECTURE.md`, `docs/DEPLOY_CONTABO.md`, `docs/DEPLOY.md`, `docs/DECISIONS.md`, `docs/PROGRESS.md`, `docs/STRESS_TEST.md`, `docs/GAP_AUDIT.md`, formal `docs/PHASE_*_REPORT.md`, `docs/FINAL_REPORT.md`, `docs/diagrams/`, `docs/contracts/`.
