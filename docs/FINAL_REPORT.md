# ARW ML Lab — One-shot finish report (interim)

**Date:** 17 Nov 2026 (IST)
**Tip:** `64952aa` — oneshot-c110 ST-OPS-07 prediction Storage purge on expired jobs
**Live frontend:** https://arw-ml-lab.vercel.app/login → **200**
**Repo:** https://github.com/ShibayanBiswas/arw-ml-lab
**Backend target:** Contabo VPS (`docs/DEPLOY_CONTABO.md`, ADR-0017) — **not yet live**

Honest interim. Contabo infra + GHCR/SSH deploy workflow are in tree. Hosted Contabo prove and full 4A→8.2 AC closure are **not** done. One-shot continued offline through ~c108 (CLE/REE/FS/DR/CLU/ANO/OPS/F*).

## Contabo move (v2.3)

| Item | Status |
|---|---|
| Docs + ADR-0017 + prune | done |
| compose.prod / Caddy / deploy.sh / bootstrap script | done |
| deploy.yml migrate → GHCR build → SSH deploy → smoke | done in repo |
| SSH bootstrap / server `.env` / known_hosts / LAB_API_URL | **blocked** — no CONTABO_HOST |
| GitHub CONTABO_USER + CONTABO_SSH_KEY + SMOKE_EDA | set |
| CI + Deploy runners | **blocked** — Actions billing/payment |

## Blocked — needs Shibayan

Exact commands: `docs/PROGRESS.md` → Blocked (Contabo `.env`, Actions billing, Supabase migrate secrets, NVIDIA_API_KEY, TradingLab).

## Next

Continue catalogue/Chunk C offline; Contabo prove resumes when host + Actions billing + migrate secrets are unblocked.
