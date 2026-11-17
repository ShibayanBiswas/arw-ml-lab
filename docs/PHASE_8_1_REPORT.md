# Phase 8.1 report — Hosted skeleton (live)

**Date:** 2026-11-15 (IST)  
**Status:** green for agent-reachable ACs; hosted API smoke blocked on Render payment

## Built

### Repo hardening
- `backend/worker/maintenance.py` — CLI `--all` with safe no-op stubs for retention/reaper until Phase 8.2
- `tests/unit/test_maintenance.py`
- `.github/workflows/ci.yml` / `deploy.yml` — deploy smoke + optional DS1 EDA via `scripts/smoke_hosted.sh`
- `docs/DEPLOY.md`, `docs/DEPLOY.md`, `docs/plans/PHASE_8_1_PLAN.md`
- ADR-0003 (TradingLab deferred; smoke scope; branch/`main`; live IDs)

### GitHub
- Private repo https://github.com/ShibayanBiswas/arw-ml-lab (`main` tracks `origin`)
- Environment `production` created
- Branch protection / rulesets: **HTTP 403** on Free private plan (needs GitHub Pro) — documented

### Supabase
- Project `arw-ml-lab` / ref `ushtfpelbpjfkjoppklz` / region `ap-south-1` / status ACTIVE_HEALTHY
- URL: `https://ushtfpelbpjfkjoppklz.supabase.co`
- Migrations applied (core, RLS, storage, try_uuid, prediction studio, hardening, security grants)
- Buckets confirmed: `datasets`, `artefacts`, `models`, `reports`, `plots`, `predictions` (private; size limits from hardening)
- Remaining manual: Pro global file size ≥ 2 GB; Auth redirect URLs for Vercel (listed in DEPLOY.md)

### Render
- Blueprint `arw-ml-lab` id `exs-dbsnkbpsrm7s73drvi90` (`autoSync=false`, repo linked)
- First plan: **failed** with `need_payment_info` on all services — no resources created
- Unblock: add payment method → plan/approve Blueprint → fill `lab-shared` secrets → deploy hooks → GitHub vars

### Vercel
- Project `arw-ml-lab` (team `shibayan-biswas-projects`), Root Directory `frontend`, framework Next.js
- Git connected to `ShibayanBiswas/arw-ml-lab`
- Env (Production): `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `NEXT_PUBLIC_LAB_API_URL` (placeholder until lab-api URL exists)
- Production deploy: **READY** — https://arw-ml-lab.vercel.app  
  Inspect: https://vercel.com/shibayan-biswas-projects/arw-ml-lab/C4zdfjMCbvMda4eFpRQhMtVzgJU7

## Acceptance criteria

| Check | Result |
|---|---|
| Blueprint services exist | **PARTIAL** — Blueprint created; services not provisioned (`need_payment_info`) |
| Migrations + RLS remote | **PASS** — applied on `ushtfpelbpjfkjoppklz`; buckets listed via SQL |
| Vercel build | **PASS** — `pnpm build` on Vercel; aliased to `arw-ml-lab.vercel.app` |
| Upload path coded | **PASS** — Phase 1 StoragePort + signed URL; live 200 MB upload not re-run (quota/time) |
| Smoke healthz + DS1 EDA | **BLOCKED** — no `lab-api` URL until Render payment; script ready: `scripts/smoke_hosted.sh` |
| AI key absent from client | **PASS** — CI bundle grep (unchanged); no NVIDIA key on Vercel |
| CI gates merges | **PARTIAL** — workflows on `main`; branch protection needs GitHub Pro |

## Local verification (real runs)

```
.\.venv\Scripts\python.exe -m pytest tests/unit/test_maintenance.py -q
..                                                                       [100%]

.\.venv\Scripts\python.exe -m pytest tests/unit/test_maintenance.py tests/golden -q --tb=line
(exit 0; golden DS3/DS22/DS30 catalogue ran; ruff: All checks passed!)

.\.venv\Scripts\ruff.exe check backend/worker/maintenance.py
All checks passed!
```

Hosted `GET /healthz`: **not computed** (Contabo VPS not bootstrapped — `CONTABO_HOST` missing; Actions billing also blocks Deploy).

## Contabo move (v2.3) — hosted smoke

| Check | Result |
|---|---|
| Docs + ADR + prune + compose/Caddy/deploy.yml | **PASS** (in repo) |
| SSH bootstrap + server `.env` | **BLOCKED** — no `CONTABO_HOST` / SSH path in local `.env` |
| GHCR build + SSH deploy + `/healthz` 200 | **BLOCKED** — host + GitHub Actions billing |
| DS1 EDA browser prove + SSE + Storage artefacts | **BLOCKED** — needs live `LAB_API_URL` |
| Restore drill + external uptime | Offline contracts ready (`OPS.RESTORE.DRILL`, `OPS.UPTIME.EXTERNAL`); live not run |

## Deviations / TODOs

1. Fill Contabo + Supabase + NVIDIA secrets in local `.env`; fix GitHub Actions billing; agent resumes bootstrap → Deploy smoke.
2. Enable GitHub Pro (or move repo to org) for branch protection requiring CI.
3. Supabase dashboard: global file size 2 GB; Auth redirect URLs from DEPLOY.md.
4. Replace Vercel `NEXT_PUBLIC_LAB_API_URL` with Contabo HTTPS hostname; set GitHub `LAB_API_URL`.
5. First production deploy used Vercel region iad1; prefer `sin1` when team settings allow.
6. Supabase advisor WARN on SECURITY DEFINER execute grants partially mitigated by follow-up migration `security_definer_grants`; keep under review in Phase 8.2.
7. Legacy Render Blueprint remains in `render.yaml` (header: legacy); Contabo is the v2.3 target.

## Self-verification checklist (§000)

- [x] Plan written and approved (option 2 live)
- [x] Built against plan; no secrets in repo/chat
- [x] ACs run or honestly blocked with evidence
- [x] No fabricated metrics
- [x] Report + PROGRESS + DECISIONS updated
- [x] Commit `phase 8.1: hosted skeleton`
- [x] STOP for user “continue”
