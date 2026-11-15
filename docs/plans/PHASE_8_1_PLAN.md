# Phase 8.1 — Hosted skeleton plan

Approved plan source: `phase_8.1_hosted_ade9fc23` (option 2 — live hosting).

## Locked decisions

- Live path: private GitHub `arw-ml-lab`, then user-confirmed Supabase → Render → Vercel.
- Secrets only in dashboards / GitHub Environments — never in chat or the repo.
- TradingLab submodule deferred to Phase 5 (ADR).
- Smoke scope: `GET /healthz` + DS1 sample EDA; full train→explain→predict deferred until Phase 2+.
- Default branch `main` to match CI/deploy triggers.
- Regions: Supabase Mumbai/Singapore; Render Singapore; Vercel `sin1`.

## Workstreams

A. Repo hardening — `maintenance` CLI, CI/deploy smoke, `docs/DEPLOY.md`, ADR  
B. GitHub — create/push private repo, branch protection, production environment secrets  
C. Supabase — Pro project, link + `db push`, buckets/auth redirects  
D. Render Blueprint + Vercel Root Directory `frontend`  
E. Verify ACs reachable in 8.1 → PHASE_8_1_REPORT → commit → STOP

## AC (8.1-reachable)

1. `render.yaml` validates; Blueprint creates lab-api, two workers, lab-beat, lab-kv.  
2. Migrations apply (remote push and/or CI/db_harness); RLS tests pass.  
3. Vercel/`pnpm build` succeeds from `frontend/`; no secrets in client bundle.  
4. Upload path is browser → signed Supabase Storage (coded); 200 MB live check documented.  
5. Smoke: healthz + DS1 EDA when workers+secrets ready.  
6. `NVIDIA_API_KEY` never on Vercel / client bundle (CI grep).  
7. CI gates merges; deploy runs migrations before Render hooks.  
8. `docs/DEPLOY.md` lists services, env vars, rollback.
