# ARW ML Lab — One-shot finish report (interim)

**Date:** 17 Nov 2026 (IST)
**Tip:** see `docs/PROGRESS.md` (oneshot through ~c228; Contabo still blocked)
**Frontend:** https://arw-ml-lab.vercel.app → READY
**Backend target:** Contabo VPS — **not live** (`docs/DEPLOY_CONTABO.md`, ADR-0017)

## Contabo (v2.3) — blocked on you

In repo: Contabo docs, prune, `docker-compose.prod.yml`, Caddy, `deploy.sh`, bootstrap script, GHCR+SSH `deploy.yml`, partial GitHub secrets (`CONTABO_USER`, `CONTABO_SSH_KEY`, `SMOKE_EDA`).

**Cannot proceed** until `docs/PROGRESS.md` → Blocked is cleared, especially:

1. https://github.com/settings/billing — Actions payments / spending limit (CI dies in ~2s)
2. Local `.env`: `CONTABO_HOST`, `CONTABO_SSH_KEY_PATH`, `ACME_EMAIL`, Supabase service/S3 keys, `NVIDIA_API_KEY`
3. `gh secret set SUPABASE_ACCESS_TOKEN` / `SUPABASE_DB_PASSWORD` `--env production` (stdin)

Then agent resumes: SSH bootstrap → server `.env` → Deploy green → DS1 EDA → FINAL prune.

## Offline one-shot (continued)

Catalogue, FE workbenches, Phase 7 reports/admin/load/ZAP, and STRESS/8.2 contracts through oneshot ~c218 (FS16–FS18 thin, Optuna/pooler, Celery recycle, REFIT/HUMILITY, hold-out reuse, restore/uptime/rate-limit/JWT/CORS/AUTH_BYPASS compose pin, Contabo DL + MAX_ROWS, atlas coverage, AI/VD numbers-only FE, SSE Caddy flush) while Contabo stayed blocked. Full hosted prove and TradingLab **parity** remain open.
