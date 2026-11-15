# Phase 2-cont-3 — SP Auth / UI parity + hosted seed

Approved before Phase 2A.

## Locked

1. Password-only login (no OTP screen / path).
2. Durable `lab_app_users` via Supabase service role on BFF (server-only).
3. Vercel `SEED_DEFAULT_PASSWORD_MAP` for all roster; never commit secrets.
4. Change password = current + new (no OTP).
5. SP Workstation auth UI same-to-same (ML Lab branding) + ThemeToggle on AuthShell.
6. After green: commit → push → Vercel READY (ADR-0006).
