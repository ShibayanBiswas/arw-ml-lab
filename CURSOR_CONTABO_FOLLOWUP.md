# ONE-SHOT: move the backend to Contabo, then finish everything (paste into Cursor Agent; Agent mode, strongest thinking model, Max mode)

You are the sole engineer on github.com/ShibayanBiswas/arw-ml-lab (main). Work AUTONOMOUSLY in Agent mode until all of this is done.
- Do NOT switch to Plan mode, do NOT stop between steps or phases, and do NOT ask me to confirm.
- Stop ONLY for a real blocker: a missing secret value, an expired login, a paid plan or account access. Write it in docs/PROGRESS.md under "Blocked — needs Shibayan" with the exact command I must run, skip that item and keep going.
- Never print, echo, log or commit secrets or private keys. Never paste them into chat.
- Do not change application logic for this move. Only add deploy and infra files and edit docs, workflows and config.

## 0. Read first
docs/DEPLOY_CONTABO.md (whole file, this is the spec), docs/adr/ADR-contabo.md, AGENTS.md, CURSOR_PROMPT.md §000, docs/ARCHITECTURE.md §39–§40 + §46, docs/STRESS_TEST.md, docs/PROGRESS.md, docs/DEPLOY.md, .github/workflows/*.yml, backend/Dockerfile, infra/docker-compose.yml, render.yaml, CURSOR_ONE_SHOT.md.

## 1. Docs first (DONE — `cd50ada`)
v2.3 Contabo DOC_EDITS applied; ADR-0017 in `docs/DECISIONS.md`; pointer on `docs/DEPLOY.md`. The one-time `docs/contabo/` kit was deleted in the prune commit.

## 1B. Repo cleanup (prune)
Delete superseded docs/junk per the Contabo prompt; keep the canonical set; record the deleted list in `docs/PROGRESS.md` Cleanup.

## 2. Server bootstrap over SSH
- Read CONTABO_HOST, CONTABO_SSH_KEY_PATH, CONTABO_BOOTSTRAP_USER (default root), CONTABO_DEPLOY_USER (default deploy), LAB_API_HOSTNAME and ACME_EMAIL from my local .env. If LAB_API_HOSTNAME is empty, use `<ip-with-dashes>.sslip.io`.
- Generate a CI-only key with `ssh-keygen -t ed25519 -N "" -f ~/.ssh/arw_ci_deploy -C arw-ci` if it is missing.
- Save the script from DEPLOY_CONTABO §3 as scripts/bootstrap_contabo.sh, scp it to the server and run it once as the bootstrap user with `CI_PUBKEY="$(cat ~/.ssh/arw_ci_deploy.pub)"`.
- Then verify, as `deploy` with my key:
  - `ssh deploy@host` works and root login fails;
  - `ufw status` shows only 22/80/443;
  - fail2ban sshd jail is active;
  - 4 GB swap;
  - `docker compose version` works.
- Get the host fingerprint with `ssh-keyscan -t ed25519` and confirm it matches `/etc/ssh/ssh_host_ed25519_key.pub` on the server.

## 3. Infra files (create only if missing; follow DEPLOY_CONTABO §5–§8 exactly)
- docker-compose.prod.yml with: caddy, lab-api, worker-light, worker-train, lab-beat, redis, and mlflow as the profile `mlflow`. Use the memory limits from §5 and `restart: unless-stopped`. Only caddy publishes ports.
- infra/caddy/Caddyfile and infra/contabo/deploy.sh (health check + rollback).
- No new Dockerfile logic: build the three images from backend/Dockerfile with REQUIREMENTS_LOCK. Add Dockerfile targets only if a build actually fails.
- Write /opt/arw-ml-lab/.env (chmod 600, owner deploy) from my local .env over scp using the §7 variable list, then shred the temp file.
  - Generate REDIS_PASSWORD with `openssl rand`.
  - JWT_SECRET must equal Vercel's.
  - NVIDIA_API_KEY goes ONLY in this file.
- render.yaml stays in the repo as legacy. Add a header comment saying so; do not delete it.

## 4. Workflow
In .github/workflows/deploy.yml, replace the `render` job with `build` (matrix: api, worker-light, worker-train → GHCR, tags sha + main, gha cache) and `deploy` (needs migrate + build; SSH + scp; deploy.sh <sha>; GHCR login with GITHUB_TOKEN piped on stdin).
- Keep the `migrate` job unchanged.
- Keep `smoke` (public https $LAB_API_URL/healthz, plus DS1 EDA when vars.SMOKE_EDA is true).
- Bump actions off Node 20.
- actionlint must pass.

## 5. Secrets and env (values from files and my .env via stdin; never on the command line or in output)
- Run `gh secret set --env production` for: CONTABO_HOST, CONTABO_USER=deploy, CONTABO_SSH_KEY (< ~/.ssh/arw_ci_deploy), CONTABO_KNOWN_HOSTS, SUPABASE_ACCESS_TOKEN, SUPABASE_PROJECT_ID, SUPABASE_DB_PASSWORD.
- Run `gh variable set` for: LAB_API_URL=https://<LAB_API_HOSTNAME>, SMOKE_EDA=false.
- Vercel (cd frontend, project arw-ml-lab, production + preview):
  - `vercel env rm` then `vercel env add NEXT_PUBLIC_LAB_API_URL` with the value piped on stdin;
  - make sure JWT_SECRET matches the server;
  - never add NVIDIA_API_KEY;
  - redeploy production.
- Server CORS_ALLOWED_ORIGINS=https://arw-ml-lab.vercel.app.

## 6. Deploy and prove it
- Commit `deploy: contabo vps via ghcr + ssh` and push.
- `gh run watch` CI, then Deploy: migrate → build → deploy → smoke must all be green. Fix and re-push until they are.
- Test rollback once: deploy a deliberately unhealthy tag on a throwaway branch with workflow_dispatch, confirm the automatic rollback, then revert.
- `curl -fsS https://<host>/healthz` must return 200 with a valid certificate. `docker compose ps` must show everything healthy, and redis must not be reachable from outside.
- In a browser, at https://arw-ml-lab.vercel.app: log in, load DS1, run the sample EDA end to end. Artefacts must appear in Supabase Storage and progress must stream over SSE.
- Set up the nightly backup cron and the external uptime check from §10–§11. Run one restore drill.
- Record the evidence in docs/PHASE_8_1_REPORT.md (hosted smoke now done) and in docs/PROGRESS.md: last green commit, live URLs, any Blocked items.

## 7. Then keep going without stopping
Continue with CURSOR_ONE_SHOT.md from its Chunk B, through every remaining phase to 8.2 and FINAL_REPORT.md.
- Read "Render" there as the Contabo VPS.
- Respect the VPS limits in DEPLOY_CONTABO §12: CPU only, one heavy job at a time, small DL defaults, GPU-only models return 422.
- After every chunk:
  - run tests, lint, types and build, plus the phase ACs, and paste the real output into the report;
  - update PROGRESS.md;
  - commit and push;
  - get CI + Deploy green;
  - check Vercel is READY and https://<host>/healthz returns 200.
- Never fabricate metrics.

## 8. Final cleanup when everything is green
After FINAL_REPORT.md: delete finished one-time prompts (`CURSOR_CONTABO_FOLLOWUP.md`, `CURSOR_KICKOFF.md`, older round prompts); keep or fold `CURSOR_PROMPT.md` / `CURSOR_ONE_SHOT.md`; re-run orphan/junk sweep; commit `chore: final prune`.
