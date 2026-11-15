# Phase 2-cont-3 report — SP Auth / UI parity + hosted seed

**Date:** 2026-11-15 (IST)  
**Status:** green for locked scope (ADR-0008)

## Built

### Auth (password-only)
- Login: email + password → `ml_session` immediately (no OTP)
- `/otp` redirects to `/login`; `POST /api/auth/verify-otp` returns 410
- Change password: current + new + confirm (`POST /api/auth/change-password`)
- Store: Supabase `lab_app_users` when `SUPABASE_SERVICE_ROLE_KEY` set; else memory + seed map
- Vercel secrets set: `JWT_SECRET`, `LAB_DEFAULT_SEED` (shared initial password for all roster), `SEED_DEFAULT_PASSWORD_MAP` (optional JSON); not in git
- Hosted smoke: `POST /api/auth/login` → **200** `ok:true`, no `otp`, `Set-Cookie` present

### UI (SP same-to-same, ML Lab branding)
- `LoginForm`, `AuthShell` + `ThemeToggle`, `AuthAccessStrip`, `AuthDisclaimerModal`, `ChangePasswordForm`
- Sidebar: Change password link; light/dark retained

## AC (real runs)

| AC | Result |
|---|---|
| Vitest auth store seed / map / change + LoginForm SP structure | **PASS** (11 tests) |
| `tsc --noEmit` | **PASS** |
| No OTP copy on login | **PASS** |
| Vercel env JWT_SECRET + LAB_DEFAULT_SEED | **SET** (production + preview) |
| Hosted login smoke (seeded password → session) | **PASS** |

### Commands

```
cd frontend && pnpm test --run
Test Files  5 passed / Tests  11 passed

cd frontend && pnpm exec tsc --noEmit
EXIT:0
```

## Hosted notes

- Add `SUPABASE_SERVICE_ROLE_KEY` (server-only) on Vercel when ready so change-password persists in `lab_app_users` across cold starts (ADR-0008). Login works with seed map alone.
- After deploy: optional `POST /api/auth/seed` with `x-seed-secret: <JWT_SECRET>` to force-overwrite hashes from the map.

## Self-check (§000)

- [x] frontend tests + tsc green
- [x] no secrets committed
- [x] push + Vercel READY (below)

### Deploy closeout

- GitHub `main`: `f9ee8b0` (`fix: use LAB_DEFAULT_SEED…`; feature `7b6fdfe`)
- Vercel production **READY**: `https://arw-ml-mir0m0282-shibayan-biswas-projects.vercel.app` (alias `https://arw-ml-lab.vercel.app`)

## Next

**Phase 2A** or further ML 2-cont on user **continue**.
