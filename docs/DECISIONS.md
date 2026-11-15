# Architecture decision records

## ADR-0003 — Phase 8.1 hosted skeleton scope (2026-11-15)

- Live path: private GitHub `arw-ml-lab`, Supabase Pro, Render Blueprint (`render.yaml`), Vercel Root Directory `frontend`.
- TradingLab git submodule **not** added in 8.1 (remains Phase 5; CI `submodules: recursive` is a no-op without `.gitmodules`).
- §39.13 sample flow “EDA → Quick train → leaderboard → explain → predict” is **deferred** until those stages exist (Phase 2+). Phase 8.1 smoke is `GET /healthz` plus optional DS1 EDA via `scripts/smoke_hosted.sh` when workers and secrets are ready.
- `lab-beat` runs `python -m backend.worker.maintenance --all` with Phase 8.1 no-op stubs; real reaper/retention in Phase 8.2.
- Default branch renamed to `main` to match CI/deploy triggers.
- Secrets only in Render / Vercel / GitHub Environment `production` dashboards — never in the repo or chat.

## ADR-0002 — Phase 1 EDA without TradingLab (2026-11-15)

- TradingLab remains Phase 5. EDA.T.BREAKS TL methods (Chow/CUSUM/SADF), TL volatility estimators, and ONC feature clustering return `not computed` with reason `tradinglab_phase_5`.
- Breaks still include `ruptures` PELT; financial stats use scipy/pandas returns metrics until Phase 5.
- `arch` and `ruptures` added to `eda.txt` so sequential EDA runs on `lab-worker-light`.
- Local `StoragePort` filesystem adapter under `.cache/uploads/` for tests without hosted Supabase.

## ADR-0001 — Phase 0 foundations (2026-11-15)

- **SP design source:** Cloned `ShibayanBiswas/sp-workstation` into `refs/sp-workstation` (git-ignored) and ported tokens/shell patterns into `frontend/`.
- **PyJWT:** Declared explicitly in `backend/requirements/api.txt` (was already a transitive of `supabase`) for JWKS verification in FastAPI.
- **Local Docker image:** Phase 0 compose builds from `api.lock.txt` for fast smoke; Render `lab-worker-train` still uses `worker-train.lock.txt` per `render.yaml`.
- **Supabase CLI:** Pinned to `3.1.0` in CI/deploy (ST-OPS-10).
- **TradingLab:** Not vendored in Phase 0 (owned by Phase 5).
