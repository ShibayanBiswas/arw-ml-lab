# Build progress (keep current — CURSOR_PROMPT.md §000 "Resume")

| Field | Value |
|---|---|
| Current phase | Contabo v2.3 (blocked on host secrets) + One-shot CLE/REE → 8.2 |
| Last completed step | oneshot-c167 **MI.TS.TARGET_TRANSFORM** (ST-ML-02 / MI-05 offline); oneshot-c165 **MI.PREPROCESS.FIT** (MI-01) |
| Last green commit | _(pending c167)_ |
| Open failures | Contabo host/SSH/.env; Supabase migrate secrets; NVIDIA_API_KEY; Deploy cannot smoke without LAB_API_URL |
| Next action | Shibayan: Contabo + Supabase + NVIDIA secrets (Blocked). Agent: ST-ML-02 remainder (MI-02/04…) / ST-UX-02 / Chunk C / Phase 7 per FINAL_REPORT |

## Blocked — needs Shibayan

| Item | Exact action |
|---|---|
| Contabo VPS + SSH | Put in local `.env`: `CONTABO_HOST=<ip>`, `CONTABO_SSH_KEY_PATH=<private key that can log in as root or deploy>`, optional `CONTABO_BOOTSTRAP_USER=root`, `CONTABO_DEPLOY_USER=deploy`, `LAB_API_HOSTNAME=` (empty → sslip.io), `ACME_EMAIL=<you@domain>` |
| CI deploy key | Already created at `~/.ssh/arw_ci_deploy` and set as `CONTABO_SSH_KEY` / `CONTABO_USER=deploy` in GitHub `production`. After bootstrap, agent will set `CONTABO_KNOWN_HOSTS` + `LAB_API_URL` |
| `NVIDIA_API_KEY` | Add to local `.env` (copied **only** to `/opt/arw-ml-lab/.env` on the VPS; never Vercel/GitHub) |
| Supabase server env for VPS | Local `.env` needs `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_JWKS_URL`, `DATABASE_URL`, `DATABASE_URL_SESSION`, S3 keys |
| `SUPABASE_ACCESS_TOKEN` | `gh secret set SUPABASE_ACCESS_TOKEN --env production --repo ShibayanBiswas/arw-ml-lab` (stdin) |
| `SUPABASE_DB_PASSWORD` | `gh secret set SUPABASE_DB_PASSWORD --env production --repo ShibayanBiswas/arw-ml-lab` (stdin) |
| TradingLab submodule | `vendor/tradinglab` for FS16–18 + AFML parity |
| GitHub Actions billing | CI/Deploy jobs die in ~2s: account payments failed or spending limit. Fix https://github.com/settings/billing then re-run Actions |

## Contabo move checklist (agent)

- [x] DOC_EDITS + ADR-0017 + DEPLOY.md v2.3 pointer (`cd50ada`)
- [x] 1B prune (`96af997`)
- [ ] SSH bootstrap + verify (**blocked** — no `CONTABO_HOST`)
- [x] compose.prod / Caddy / deploy.sh in repo (`9419aa3`); server `.env` **blocked**
- [x] deploy.yml GHCR+SSH (`9419aa3`); actionlint clean
- [ ] gh secrets/vars complete (`CONTABO_USER`, `CONTABO_SSH_KEY`, `SMOKE_EDA` set; host/known_hosts/LAB_API_URL/Supabase tokens still missing)
- [ ] Vercel `NEXT_PUBLIC_LAB_API_URL` (**blocked** — no hostname)
- [ ] Deploy green + smoke + rollback + backup cron
- [ ] One-shot remainder → FINAL_REPORT
- [ ] Final prune

## Cleanup

| Deleted | Reason |
|---|---|
| `docs/contabo/` (DOC_EDITS.md) | One-time Contabo doc-edit kit; applied in `cd50ada` |
| `docs/TODO.md` | Stale OTP/lock TODOs; open items live in this file |
| `docs/runbooks/HOSTED_CHECKLIST.md` | Overlapped `DEPLOY.md` / `DEPLOY_CONTABO.md`; unique ticks merged into `DEPLOY.md` Live status |
| one-shot helper scripts under `scripts/_*.py` | Temporary Contabo edit/prune helpers |
| empty `docs/runbooks/` | Emptied after checklist removal |

Kept: phase plans + reports, `docs/adr/ADR-contabo.md`, diagrams 01–21, `GAP_AUDIT`, `FINAL_REPORT`, contracts.

## One-shot commits (16–17 Nov 2026)
A deploy gate → B.1–B.3 → C.1–C.69 (CLE/REE/F* in progress)

See docs/FINAL_REPORT.md for the full table.
