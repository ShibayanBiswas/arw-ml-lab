# ARW ML Lab — One-shot finish report (interim)

**Date:** 18 Nov 2026 (IST)
**Tip:** see `docs/PROGRESS.md` (oneshot through ~c280; Contabo still blocked)
**Frontend:** https://arw-ml-lab.vercel.app → READY
**Backend target:** Contabo VPS — **not live** (`docs/DEPLOY_CONTABO.md`, ADR-0017)
**Offline hardening ledger:** `docs/PHASE_8_2_REPORT.md`

## Contabo (v2.3) — blocked on you

In repo: Contabo docs, prune, `docker-compose.prod.yml`, Caddy, `deploy.sh`, bootstrap script, GHCR+SSH `deploy.yml`, partial GitHub secrets (`CONTABO_USER`, `CONTABO_SSH_KEY`, `SMOKE_EDA`, `SUPABASE_PROJECT_ID`).

**Cannot prove hosted** until `docs/PROGRESS.md` → Blocked is cleared, especially:

1. https://github.com/settings/billing — Actions payments / spending limit (CI dies in ~2s with empty job steps)
2. Local `.env`: `CONTABO_HOST`, `CONTABO_SSH_KEY_PATH`, `ACME_EMAIL`, Supabase service/S3 keys, `NVIDIA_API_KEY`
3. `gh secret set SUPABASE_ACCESS_TOKEN` / `SUPABASE_DB_PASSWORD` / `CONTABO_HOST` / `CONTABO_KNOWN_HOSTS` `--env production` (stdin)
4. After hostname exists: Vercel `NEXT_PUBLIC_LAB_API_URL` + Deploy smoke + DS1 EDA + rollback + backup cron

Then agent resumes: SSH bootstrap → server `.env` → Deploy green → DS1 EDA → FINAL prune (`chore: final prune`).

## Offline one-shot (continued while Contabo blocked)

Catalogue, FE workbenches, Phase 7 reports/admin/load/ZAP, Prediction Studio §45, DL UQ, and STRESS/8.2 contracts through oneshot ~c280, including:

- SoftTimeLimit mid-run `PartialHolder` (train/tune/predict/eda)
- Predict Redis/memory cancel flags + Contabo `LAB_CANCEL_USE_REDIS`
- Contabo CPU DL quick/balanced presets
- REP.T.BUNDLE runnable `reproduce.py`
- OPS.JSON.LOGS + OTLP exporter pin + Celery OTel wire
- Admin workers/queues panel (`OPS.ADMIN.WORKERS`)
- Locust auth opt-in; in-lab purged/CPCV/PBO oracles (TradingLab parity still skip-gated)
- Module journey HTTP e2e + Playwright journey gates

Full Contabo prove, Actions green, TradingLab **parity** submodule, and step-8 final prune remain open.
