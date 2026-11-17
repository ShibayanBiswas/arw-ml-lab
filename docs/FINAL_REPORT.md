# ARW ML Lab — One-shot finish report (interim)

**Date:** 17 Nov 2026 (IST)  
**Tip:** see `docs/PROGRESS.md` (oneshot through ~c87; Contabo infra in repo)  
**Live frontend:** https://arw-ml-lab.vercel.app/login → **200**  
**Repo:** https://github.com/ShibayanBiswas/arw-ml-lab  
**Backend target:** Contabo VPS (`docs/DEPLOY_CONTABO.md`, ADR-0017) — **not yet live**

Honest interim closeout. Contabo docs + compose + GHCR/SSH deploy workflow are in tree. Hosted Contabo prove and full 4A→8.2 AC closure are **not** done.

## Contabo move (v2.3)

| Item | Status |
|---|---|
| Docs + ADR-0017 | done (`cd50ada`) |
| Prune | done (`96af997`) |
| `docker-compose.prod.yml`, Caddyfile, `deploy.sh`, bootstrap script | done (`9419aa3`) |
| `deploy.yml` migrate → build (GHCR) → deploy (SSH) → smoke | done in repo; actionlint clean |
| SSH bootstrap / server `.env` / known_hosts / `LAB_API_URL` | **blocked** — no `CONTABO_HOST` in local `.env` |
| GitHub `CONTABO_USER` + `CONTABO_SSH_KEY` + `SMOKE_EDA` | set |
| CI + Deploy runners | **blocked** — Actions billing / payment failure |

## Per-phase status

| Phase | Status | Evidence |
|---|---|---|
| 0–2B, 8.1 thin | done | `docs/PHASE_*_REPORT.md` |
| 2 deepen | partial | CLE.P / REE.P catalogues advanced through oneshot-c87+ |
| 2A deepen | partial | train-window-only scaler; DeepWorkbench |
| 3 deepen | partial | LIME/DiCE/ALE/EBM + ONNX/skops; Anchors off (BSL) |
| 3A deepen | partial | PV02/03/10/14/15, Celery batch ≤1M, cancel |
| 4 / 4A | partial | F1–F25 classical + F13/F16/F18/F21/F23 |
| 5B | partial | FS1–FS15, FS19–20; FS16–18 deferred (TradingLab) |
| 5 / 5A | partial | purged/CPCV + PBO; WFO Ridge retune |
| 6 / 6A / 6B | partial | unsupervised + VLM guards + catalogues |
| 7 / 8.2 | partial | reports/e2e/Locust/ZAP/Playwright opt-in; Contabo path replaces Render smoke |

## CI / Deploy / Vercel

| System | Status | Notes |
|---|---|---|
| CI | last green `ebd29b1` (c64); later runs fail at start | Actions: payments failed / spending limit — https://github.com/settings/billing |
| Deploy | Contabo path in workflow | needs host secrets + Actions billing + Supabase migrate secrets |
| Vercel | READY / **200** | https://arw-ml-lab.vercel.app — point `NEXT_PUBLIC_LAB_API_URL` at Contabo HTTPS when live |

## Blocked — needs Shibayan

1. Fix GitHub Actions billing: https://github.com/settings/billing  
2. Local `.env`: `CONTABO_HOST`, `CONTABO_SSH_KEY_PATH`, `ACME_EMAIL`, optional `LAB_API_HOSTNAME`, plus Supabase service/S3 keys and `NVIDIA_API_KEY`  
3. `gh secret set SUPABASE_ACCESS_TOKEN` / `SUPABASE_DB_PASSWORD` `--env production` (stdin)  
4. After bootstrap: agent sets `CONTABO_KNOWN_HOSTS`, `LAB_API_URL`, Vercel `NEXT_PUBLIC_LAB_API_URL`  
5. `vendor/tradinglab` for FS16–18 + AFML parity  

Exact commands live in `docs/PROGRESS.md` → Blocked.

## Next

Continue CLE/REE/Chunk C offline; Contabo prove resumes when host + Actions billing + migrate secrets are unblocked.
