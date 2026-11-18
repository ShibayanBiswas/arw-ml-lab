# Phase 8.2 — Production hardening (offline ledger)

**Status:** offline kit advanced through oneshot-c278; Contabo hosted prove **blocked** (see `docs/PROGRESS.md` → Blocked).

## §39.13 AC (offline vs blocked)

| AC | Offline | Hosted Contabo |
|---|---|---|
| Contabo compose / GHCR deploy / Caddy | repo files + actionlint | blocked — CONTABO_HOST + Actions billing |
| `supabase db push` + RLS CI | migrations + harness | blocked — SUPABASE_ACCESS_TOKEN / DB password |
| Vercel frontend READY | yes (arw-ml-lab.vercel.app) | NEXT_PUBLIC_LAB_API_URL wait Contabo hostname |
| 200 MB CSV → Storage | contracts + upload guards | blocked — no live API |
| DS1 EDA→train→explain→predict + SSE | offline unit/golden | blocked — Contabo smoke |
| Optuna resume after worker kill | storage URL + resume tests | blocked — live worker |
| AI numbers-only ≤10 s; no NVIDIA on Vercel | resilient_chat + SEC tests | NVIDIA_API_KEY still missing for live |
| CI blocks merges; deploy migrate→build→deploy→smoke | workflows exist | Actions billing kills jobs in ~2s |
| DEPLOY.md / DEPLOY_CONTABO.md | yes | — |
| STRESS_TEST rows | offline contracts through c275 | hosted prove rows still open |
| Restore drill | script + unit contract | blocked — no VPS rclone cron |

## Offline closed this phase (selected)

- SoftTimeLimit mid-run PartialHolder (train/tune/predict) — c272–c273
- Predict Redis/memory cancel flags — c273
- REP.T.BUNDLE runnable `reproduce.py` — c274
- JSON logs + OTLP pin + Celery instrument — c275
- Admin workers / Locust auth / in-lab finance oracles — c276
- Playwright journey gates + tune log context — c278
- Contabo DL presets — c271

## Still blocked on Shibayan

See `docs/PROGRESS.md` Blocked table (Contabo SSH, Actions billing, Supabase migrate secrets, NVIDIA_API_KEY, Vercel team authorize, TradingLab submodule parity).
