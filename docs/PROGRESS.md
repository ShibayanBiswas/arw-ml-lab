# Build progress (keep current — CURSOR_PROMPT.md §000 "Resume")

| Field | Value |
|---|---|
| Current phase | Contabo v2.3 move → then One-shot remainder → 8.2 |
| Last completed step | docs: Contabo DOC_EDITS + ADR-0017 applied |
| Last green commit | ebd29b1 (oneshot-c64; Deploy Contabo not yet proven) |
| Open failures | Contabo host/SSH/.env secrets missing; Supabase migrate secrets; NVIDIA_API_KEY |
| Next action | Shibayan: fill Contabo + AI secrets (see Blocked). Agent: prune → infra → workflow; resume when host reachable |

## Blocked — needs Shibayan

| Item | Exact action |
|---|---|
| Contabo VPS + SSH | Put in local `.env`: `CONTABO_HOST=<ip>`, `CONTABO_SSH_KEY_PATH=<path to private key that can still log in as root or deploy>`, optional `CONTABO_BOOTSTRAP_USER=root`, `CONTABO_DEPLOY_USER=deploy`, `LAB_API_HOSTNAME=` (empty → sslip.io), `ACME_EMAIL=<you@domain>` |
| CI deploy key | Agent will create `~/.ssh/arw_ci_deploy` once host is set; you only need your bootstrap key path in `.env` |
| `NVIDIA_API_KEY` | Add to local `.env` (agent copies **only** to `/opt/arw-ml-lab/.env` on the VPS; never Vercel/GitHub) |
| Supabase server env | Ensure local `.env` also has `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_JWKS_URL`, `DATABASE_URL`, `DATABASE_URL_SESSION`, S3 keys for the VPS `.env` |
| `SUPABASE_ACCESS_TOKEN` | `gh secret set SUPABASE_ACCESS_TOKEN --env production --repo ShibayanBiswas/arw-ml-lab` (stdin) |
| `SUPABASE_DB_PASSWORD` | `gh secret set SUPABASE_DB_PASSWORD --env production --repo ShibayanBiswas/arw-ml-lab` (stdin) |
| `SUPABASE_PROJECT_ID` | `gh secret set SUPABASE_PROJECT_ID --env production --repo ShibayanBiswas/arw-ml-lab` (value `ushtfpelbpjfkjoppklz` via stdin) |
| TradingLab submodule | `vendor/tradinglab` for FS6–19 + AFML parity |

## Contabo move checklist (agent)

- [x] DOC_EDITS + ADR-0017 + DEPLOY.md v2.3 pointer
- [ ] 1B prune
- [ ] SSH bootstrap + verify
- [ ] compose.prod / Caddy / deploy.sh / server `.env`
- [ ] deploy.yml GHCR+SSH
- [ ] gh secrets/vars + Vercel `NEXT_PUBLIC_LAB_API_URL`
- [ ] Deploy green + smoke + rollback drill + backup cron
- [ ] One-shot remainder → FINAL_REPORT
- [ ] Final prune

## Cleanup

_(filled in the prune commit)_

## One-shot commits (16 Nov 2026)
A deploy gate → B.1–B.3 → C.1–C.64 (CLE/REE/F* in progress)

See docs/FINAL_REPORT.md for the full table.
