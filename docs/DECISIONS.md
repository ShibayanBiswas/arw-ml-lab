# Architecture decision records

## ADR-0001 — Phase 0 foundations (2026-11-15)

- **SP design source:** Cloned `ShibayanBiswas/sp-workstation` into `refs/sp-workstation` (git-ignored) and ported tokens/shell patterns into `frontend/`.
- **PyJWT:** Declared explicitly in `backend/requirements/api.txt` (was already a transitive of `supabase`) for JWKS verification in FastAPI.
- **Local Docker image:** Phase 0 compose builds from `api.lock.txt` for fast smoke; Render `lab-worker-train` still uses `worker-train.lock.txt` per `render.yaml`.
- **Supabase CLI:** Pinned to `3.1.0` in CI/deploy (ST-OPS-10).
- **TradingLab:** Not vendored in Phase 0 (owned by Phase 5).
