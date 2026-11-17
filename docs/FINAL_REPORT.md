# ARW ML Lab — One-shot finish report (interim)

**Date:** 17 Nov 2026 (IST)
**Tip:** `c020ffa` — oneshot-c129 FE.WB.UNSUP_ANOM
**Live frontend:** https://arw-ml-lab.vercel.app/login → **200**
**Repo:** https://github.com/ShibayanBiswas/arw-ml-lab
**Backend target:** Contabo VPS (`docs/DEPLOY_CONTABO.md`, ADR-0017) — **not yet live**

## Contabo (v2.3) — repo ready, host blocked

Docs, prune, `docker-compose.prod.yml`, Caddy, `deploy.sh`, bootstrap script, and GHCR+SSH `deploy.yml` are on `main`. Cannot bootstrap or smoke until you unblock the items in `docs/PROGRESS.md` → **Blocked**.

Critical: **GitHub Actions billing** (jobs fail immediately) + **CONTABO_HOST** / SSH key path + Supabase migrate secrets + `NVIDIA_API_KEY` in local `.env` only.

## One-shot offline progress

Continued Chunk C catalogue work through oneshot ~c127 (CLE/REE/FS/CLU/DR/ANO/OPS/F*). Full 4A→8.2 AC closure and hosted Contabo prove remain open.

## Next

Unblock Contabo + Actions billing (PROGRESS), then agent resumes SSH bootstrap → server `.env` → Deploy green → browser DS1 EDA → FINAL prune.
