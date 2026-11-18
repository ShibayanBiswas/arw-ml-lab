# Build progress

| Field | Value |
|---|---|
| Tip | `d1f6b61` wind-up final |
| Frontend | https://arw-ml-lab.vercel.app — login **200** |
| Backend | Contabo VPS — **not live** |
| Local API smoke | TestClient `/healthz` **200** seed 42; catalog **83** algorithms; samples **200** |
| CI / Deploy | **Failing** — Actions billing (~2s empty jobs); Deploy skipped |
| Next action | Shibayan clears Blocked below → agent bootstraps Contabo → Deploy green → DS1 EDA |

## Blocked — needs Shibayan

| Item | Exact action |
|---|---|
| Contabo VPS + SSH | Local `.env`: `CONTABO_HOST`, `CONTABO_SSH_KEY_PATH`, `ACME_EMAIL`, optional `LAB_API_HOSTNAME` (empty → sslip.io) |
| GitHub `production` secrets | Still missing: `CONTABO_HOST`, `CONTABO_KNOWN_HOSTS`, `SUPABASE_ACCESS_TOKEN`, `SUPABASE_DB_PASSWORD` (stdin via `gh secret set --env production`) |
| `NVIDIA_API_KEY` | Local `.env` only → copy to `/opt/arw-ml-lab/.env` on VPS (never Vercel) |
| Supabase server env | `SUPABASE_SERVICE_ROLE_KEY`, JWKS, `DATABASE_URL` (+ session), S3 keys in local `.env` for VPS scp |
| GitHub Actions billing | https://github.com/settings/billing — payment / raise spend limit |
| Vercel team authorize | Needed to set `NEXT_PUBLIC_LAB_API_URL` after Contabo hostname exists |
| TradingLab submodule | `vendor/tradinglab` for parity tests (thin FS16–18 already online) |

## Contabo checklist

- [x] Docs + ADR + prune kit + `docker-compose.prod.yml` / Caddy / `deploy.sh` / GHCR+SSH workflow
- [ ] SSH bootstrap + server `.env`
- [ ] Secrets/vars complete + Vercel `NEXT_PUBLIC_LAB_API_URL`
- [ ] Deploy green + smoke + rollback + backup cron + DS1 EDA
- [x] Offline oneshot → `docs/FINAL_REPORT.md` + docs wind-up prune

## Cleanup (this wind-up)

| Deleted | Reason |
|---|---|
| `docs/PHASE_ONESHOT_C*.md` (~252) | One-shot micro-reports; facts folded into FINAL_REPORT |
| `docs/plans/PHASE_*.md`, `build_plan_page.tsx` | Superseded by shipped code + `docs/plans/BUILD_PLAN.md` |
| `CURSOR_KICKOFF.md`, `CURSOR_CONTABO_FOLLOWUP.md` | Finished one-time prompts |

**Kept:** formal `docs/PHASE_*_REPORT.md` (0–8.2), `FINAL_REPORT.md`, ARCHITECTURE / DEPLOY* / STRESS / GAP_AUDIT / diagrams / contracts, `CURSOR_PROMPT.md`, `CURSOR_ONE_SHOT.md`.
