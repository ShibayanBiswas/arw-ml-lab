# Architecture decision records

## ADR-0004 — Phase 1A intake rule-based only (2026-11-15)

- LLM adjudicator (§33.9) deferred to Phase 6; Phase 1A ships detectors D1–D8 + validator behind the same proposal schema.
- Financial targets are JSON builders only (`triple_barrier`, `fwd_log_return`, …); TradingLab remains Phase 5 (extends ADR-0002).
- `lab.intake.run` must not overwrite the Phase-1 `TaskSpec` on `DATASET_STORE`; confirmed `task_spec` attaches to the experiment via confirm.
- Large-frame intake uses a ≤20k stride sample for detectors; full `n_rows` is preserved on the profile.
- New pins: `exchange-calendars==4.11.1`, `rapidfuzz==3.14.1` (`eda.txt` / §44); `worker-light.lock.txt` recompiled for 3.12.

## ADR-0003 — Phase 8.1 hosted skeleton scope (2026-11-15)

- Live path: private GitHub `arw-ml-lab`, Supabase Pro, Render Blueprint (`render.yaml`), Vercel Root Directory `frontend`.
- TradingLab git submodule **not** added in 8.1 (remains Phase 5; CI `submodules: recursive` is a no-op without `.gitmodules`).
- §39.13 sample flow “EDA → Quick train → leaderboard → explain → predict” is **deferred** until those stages exist (Phase 2+). Phase 8.1 smoke is `GET /healthz` plus optional DS1 EDA via `scripts/smoke_hosted.sh` when workers and secrets are ready.
- `lab-beat` runs `python -m backend.worker.maintenance --all` with Phase 8.1 no-op stubs; real reaper/retention in Phase 8.2.
- Default branch renamed to `main` to match CI/deploy triggers.
- Secrets only in Render / Vercel / GitHub Environment `production` dashboards — never in the repo or chat.
- **Branch protection:** GitHub Free on a **private** repo returns HTTP 403 for classic protection and rulesets (“Upgrade to GitHub Pro”). Documented in DEPLOY; enable after Pro or org-owned repo.
- **Render Blueprint:** created (`exs-dbsnkbpsrm7s73drvi90`) with `autoSync=false`; first plan fails with `need_payment_info` until a payment method is on the Render workspace. Approve Blueprint only after payment + cost OK.
- **Supabase:** project `ushtfpelbpjfkjoppklz` (`ap-south-1`); migrations applied via MCP (not CLI `db push`). Hosted global file-size 2 GB still requires Pro plan + dashboard toggle.
- **Vercel:** project `arw-ml-lab`, Root Directory `frontend`, production `https://arw-ml-lab.vercel.app`.

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
