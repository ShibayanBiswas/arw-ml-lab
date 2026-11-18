# Build progress (keep current — CURSOR_PROMPT.md §000 "Resume")

| Field | Value |
|---|---|
| Current phase | Contabo v2.3 (blocked on host secrets) + One-shot CLE/REE → 8.2 |
| Last completed step | oneshot-c267 decision eval-harness API; Contabo still blocked |
| Last green commit | 9cd4d8d |
| Open failures | Contabo host/SSH/.env; Supabase migrate secrets; NVIDIA_API_KEY; Deploy cannot smoke without LAB_API_URL; Actions billing; TradingLab parity (submodule) |
| Next action | Shibayan: Contabo + Supabase + NVIDIA + Actions billing (Blocked). Agent: continue 8.2 offline gaps; TradingLab parity when submodule present |

## Blocked — needs Shibayan

| Item | Exact action |
|---|---|
| Contabo VPS + SSH | Put in local `.env`: `CONTABO_HOST=<ip>`, `CONTABO_SSH_KEY_PATH=<private key that can log in as root or deploy>`, optional `CONTABO_BOOTSTRAP_USER=root`, `CONTABO_DEPLOY_USER=deploy`, `LAB_API_HOSTNAME=` (empty → sslip.io), `ACME_EMAIL=<you@domain>` — then agent runs bootstrap and `gh secret set CONTABO_HOST` / `CONTABO_KNOWN_HOSTS` |
| CI deploy key | Present in GitHub `production`: `CONTABO_SSH_KEY`, `CONTABO_USER`. Still missing env secrets: `CONTABO_HOST`, `CONTABO_KNOWN_HOSTS`, `SUPABASE_ACCESS_TOKEN`, `SUPABASE_DB_PASSWORD`. After bootstrap set `LAB_API_URL` variable |
| `NVIDIA_API_KEY` | Add to local `.env` (copied **only** to `/opt/arw-ml-lab/.env` on the VPS; never Vercel/GitHub) |
| Supabase server env for VPS | Local `.env` needs `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_JWKS_URL`, `DATABASE_URL`, `DATABASE_URL_SESSION`, S3 keys |
| `SUPABASE_ACCESS_TOKEN` | `gh secret set SUPABASE_ACCESS_TOKEN --env production --repo ShibayanBiswas/arw-ml-lab` (stdin) |
| `SUPABASE_DB_PASSWORD` | `gh secret set SUPABASE_DB_PASSWORD --env production --repo ShibayanBiswas/arw-ml-lab` (stdin) |
| TradingLab submodule | `vendor/tradinglab` for **parity** tests vs thin FS16–18 (SADF/trendscan/MA-cross already online) |
| Vercel MCP / CLI team scope | Approve: https://vercel.com/sso/session-requests/gi977x3MZbHDi41KWqHIvLdCURztMlhs (single-use, ~10 min) or `vercel link` in `frontend/` — needed before setting `NEXT_PUBLIC_LAB_API_URL` after Contabo hostname exists |
| GitHub Actions billing | CI/Deploy still die in ~2–4s (e.g. `44087280966`). Fix https://github.com/settings/billing — add payment method and/or raise Actions budget / clear “Stop usage when budget limit is reached”, then re-run failed workflows |

## Contabo move checklist (agent)

- [x] DOC_EDITS + ADR-0017 + DEPLOY.md v2.3 pointer (`cd50ada`)
- [x] 1B prune (`96af997`)
- [ ] SSH bootstrap + verify (**blocked** — no `CONTABO_HOST`)
- [x] compose.prod / Caddy / deploy.sh in repo (`9419aa3`); server `.env` **blocked**
- [x] deploy.yml GHCR+SSH (`9419aa3`); actionlint clean
- [ ] gh secrets/vars complete (`CONTABO_USER`, `CONTABO_SSH_KEY`, `SMOKE_EDA=false` set; still missing `CONTABO_HOST`, `CONTABO_KNOWN_HOSTS`, `LAB_API_URL`, `SUPABASE_ACCESS_TOKEN`, `SUPABASE_DB_PASSWORD`)
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
