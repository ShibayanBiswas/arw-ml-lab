# Build progress

| Field | Value |
|---|---|
| Tip | `c2e636b` phase-MD purge + verify |
| Frontend | https://arw-ml-lab.vercel.app — login **200**; `/train` **307**→login |
| Backend | Contabo VPS — **not live** |
| Local API smoke | TestClient `/healthz` **200** seed 42; catalog **83**; samples **200**; OpenAPI **107** paths |
| Local unit | **732 passed / 4 failed** — failures are Windows memory/tkinter env (EDA/Intake 1M benches, EBM joblib, REE validation curve), not app logic |
| Frontend tsc | **Pass** |
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

## Cleanup

| Deleted | Reason |
|---|---|
| `docs/PHASE_ONESHOT_C*.md` (~252) | One-shot micro-reports; facts in FINAL_REPORT |
| All `docs/PHASE_*_REPORT.md` | Historical phase reports removed; status lives in FINAL_REPORT + PROGRESS |
| `docs/plans/PHASE_*.md`, kickoff/followup prompts | Superseded |

**Canonical docs:** `README.md`, `AGENTS.md`, `docs/FINAL_REPORT.md`, `docs/PROGRESS.md`, `docs/ARCHITECTURE.md`, `docs/DEPLOY_CONTABO.md`, `docs/STRESS_TEST.md`, `docs/GAP_AUDIT.md`, `docs/DECISIONS.md`, diagrams/contracts.
