# Deploy runbook: lab backend on a Contabo Cloud VPS (primary backend target, v2.3)

Status: primary backend target from 16 Nov 2026 (IST); see ADR `docs/adr/ADR-contabo.md` and diagram `docs/diagrams/21_contabo_deploy.png`.
Frontend stays on **Vercel**, database/auth/storage stay on **Supabase**. **Render** (`render.yaml`) is the **alternative / legacy** path; keep the file, do not delete it.
Scope: docs only. The files named below (`docker-compose.prod.yml`, `infra/caddy/Caddyfile`, Dockerfile targets, the SSH deploy job) are **designed here and created by Cursor** (see `CURSOR_CONTABO_FOLLOWUP.md`).

Contents
1. User section: how to get a Contabo server and hand it to Cursor
2. Target topology
3. Server hardening (Ubuntu 24.04) + `scripts/bootstrap_contabo.sh` (documented script)
4. Docker + compose plugin
5. `docker-compose.prod.yml` design and memory budget (8 GB)
6. Caddy (HTTPS) and hostname
7. Server env file `/opt/arw-ml-lab/.env`
8. CI/CD: GitHub Actions → GHCR → SSH deploy with health check + rollback
9. Secrets, variables, Vercel env, CORS
10. Backups
11. Monitoring and logs
12. Operations: restart policy, cost, limits, troubleshooting
13. Acceptance criteria

---

## 1. USER SECTION — How to get a Contabo server and hand it to Cursor

Do these steps once. After step 6, Cursor (with `CURSOR_CONTABO_FOLLOWUP.md`) does everything else on its own: hardening, Docker, HTTPS, GitHub secrets, Vercel env, deploys and smoke tests.

**1. Make an SSH key on your Windows PC** (PowerShell):

```powershell
ssh-keygen -t ed25519 -f $HOME\.ssh\contabo_arw -C "arw-ml-lab contabo"
# press Enter twice for no passphrase (Cursor must be able to use it unattended),
# or set a passphrase and load it into ssh-agent:  Get-Service ssh-agent | Set-Service -StartupType Automatic; Start-Service ssh-agent; ssh-add $HOME\.ssh\contabo_arw
Get-Content $HOME\.ssh\contabo_arw.pub   # this is the PUBLIC key you paste into Contabo
```

Never share or commit `contabo_arw` (no `.pub`): that is the private key.

**2. Order the server** at contabo.com → VPS:
- Plan: **Cloud VPS 10** (4 vCPU, 8 GB RAM, 75 GB NVMe; about EUR 4.50–6.60/month). Contabo renames tiers from time to time; if "Cloud VPS 10" is not listed, pick the tier with **4 vCPU / 8 GB RAM** (shown in Nov 2026 as "Cloud VPS 4", 100 GB SSD, EUR 4.40/month). Do not pick less than 8 GB RAM.
- Region: **India (Mumbai)** if offered, else **Singapore (Asia)**. Both add a small monthly location fee; Mumbai gives the lowest latency to the team and to Supabase `ap-south-1`.
- Image: **Ubuntu 24.04** (plain OS, no panel / no Plesk / no cPanel).
- Login: set a strong root password. If the order form (or Customer Control Panel → *Secrets management*) offers **SSH key**, paste the contents of `contabo_arw.pub` there.
- Extras: none required. Optional: an extra snapshot slot; Object Storage only if you want off-site backups there (§10).
- Pay; Contabo emails the **IP address** and the root login once the server is ready (usually minutes, sometimes a few hours).

**3. If you could not add the key in the order form**, install it once with the emailed root password:

```powershell
type $HOME\.ssh\contabo_arw.pub | ssh root@<SERVER_IP> "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"
ssh -i $HOME\.ssh\contabo_arw root@<SERVER_IP> "echo ok"     # must print ok without asking for a password
```

**4. Tell Cursor where the server is**: add to the repo's local `.env` (already gitignored; never commit it):

```dotenv
CONTABO_HOST=<SERVER_IP>
CONTABO_SSH_KEY_PATH=C:\Users\shiba\.ssh\contabo_arw
CONTABO_BOOTSTRAP_USER=root
CONTABO_DEPLOY_USER=deploy
LAB_API_HOSTNAME=            # leave empty to use <ip-with-dashes>.sslip.io, or e.g. api.yourdomain.com
ACME_EMAIL=you@anandrathi.com
```

Also keep the values Cursor needs to fill the server env (`SUPABASE_*`, `DATABASE_URL`, `JWT_SECRET` matching Vercel, `NVIDIA_API_KEY`, `SENTRY_DSN`) in that same local `.env`. Cursor copies them to the server file without printing them.

**5. Log the CLIs in once** (in the Cursor terminal):

```powershell
gh auth login          # GitHub.com, HTTPS, login with browser; scopes: repo, workflow, write:packages
vercel login           # then, in frontend/:  vercel link  (project arw-ml-lab)
supabase login         # used for SUPABASE_ACCESS_TOKEN / migration checks
```

**6. Optional: your own domain.** In your DNS add an `A` record `api.<yourdomain>` → `<SERVER_IP>` and put `LAB_API_HOSTNAME=api.<yourdomain>` in `.env`. Without a domain Cursor uses the free `https://<ip-with-dashes>.sslip.io` hostname (e.g. `https://203-0-113-10.sslip.io`); Caddy gets a Let's Encrypt certificate for it automatically.

**7. Paste `CURSOR_CONTABO_FOLLOWUP.md` into Cursor Agent.** You only come back if Cursor writes a line under "Blocked — needs Shibayan" in `docs/PROGRESS.md` (e.g. a missing key value or an expired login).

What Cursor will never need from you in chat: passwords, keys or tokens. They stay in files (`.env`, `~/.ssh`) and in GitHub/Vercel secret stores.

---

## 2. Target topology

```
Browser ──HTTPS──▶ Vercel (Next.js, frontend/) ──HTTPS + Bearer JWT (AUTH_MODE=bff)──▶ https://<LAB_API_HOSTNAME>
   │                                                                                        │
   └──signed upload URL──▶ Supabase Storage                         Contabo Cloud VPS (Ubuntu 24.04, Docker)
                                                                     ├─ caddy        :80/:443  (TLS, reverse proxy → lab-api:8000)
                                                                     ├─ lab-api      FastAPI/uvicorn (internal only)
                                                                     ├─ worker-light Celery q.ingest,q.eda,q.insights,q.report,q.predict.batch
                                                                     ├─ worker-train Celery q.train.cpu,q.tune,q.explain,q.forecast,q.predict.heavy
                                                                     ├─ lab-beat     hourly `python -m backend.worker.maintenance --all`
                                                                     ├─ redis        broker/cache (password, AOF, noeviction, no public port)
                                                                     └─ mlflow       optional (profile `mlflow`), artefacts in Supabase Storage
                                       workers/api ──▶ Supabase Postgres + Storage (ap-south-1)   ──▶ NVIDIA API catalog (key on VPS only)
```

GitHub Actions: `ci.yml` (unchanged) → `deploy.yml`: `migrate` (Supabase, unchanged) + `build` (3 images → GHCR) → `deploy` (SSH, pull, up, health check, rollback) → `smoke` (public `/healthz`).

## 3. Server hardening (Ubuntu 24.04)

Target state:
| Item | Setting |
|---|---|
| Users | non-root `deploy` (sudo, member of `docker`); root login disabled |
| SSH | keys only: `PasswordAuthentication no`, `KbdInteractiveAuthentication no`, `PermitRootLogin no`, `MaxAuthTries 3`; port 22 |
| Firewall | `ufw default deny incoming`, allow `22/tcp`, `80/tcp`, `443/tcp` only. Docker publishes only Caddy's 80/443; every other service has **no `ports:`** (Docker bypasses ufw for published ports, so never publish redis/api) |
| Brute force | `fail2ban` with the `sshd` jail (5 tries / 10 min → 1 h ban) |
| Patching | `unattended-upgrades` (security pocket), automatic reboot **off** (reboot manually in a quiet window; `needrestart` reports) |
| Memory | 4 GB swapfile, `vm.swappiness=10` |
| Time | `timedatectl set-timezone UTC` (logs in UTC; reports convert to IST) |
| Logs | Docker `json-file` with `max-size 10m`, `max-file 3` (§11) |

Safety rule while hardening: keep the current SSH session open, open a **second** session as `deploy` with the key, and only then restart `ssh`. The script does this check itself (step 9) before it locks root out.

### `scripts/bootstrap_contabo.sh` (documented script; run once as root; not wired into code or CI)

```bash
#!/usr/bin/env bash
# Bootstrap + harden a fresh Contabo Ubuntu 24.04 VPS for ARW ML Lab.
# Usage (as root):  DEPLOY_USER=deploy CI_PUBKEY="ssh-ed25519 AAAA... arw-ci" bash bootstrap_contabo.sh
# Idempotent: safe to re-run.
set -euo pipefail
DEPLOY_USER="${DEPLOY_USER:-deploy}"
APP_DIR=/opt/arw-ml-lab
export DEBIAN_FRONTEND=noninteractive

# 1. Packages and patches
apt-get update -y && apt-get upgrade -y
apt-get install -y ca-certificates curl gnupg ufw fail2ban unattended-upgrades needrestart jq git htop

# 2. Deploy user with the same key(s) root has, plus the CI deploy key
id "$DEPLOY_USER" >/dev/null 2>&1 || adduser --disabled-password --gecos "" "$DEPLOY_USER"
usermod -aG sudo "$DEPLOY_USER"
echo "$DEPLOY_USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/90-$DEPLOY_USER   # unattended ops by Cursor; see note below
chmod 440 /etc/sudoers.d/90-$DEPLOY_USER
install -d -m 700 -o "$DEPLOY_USER" -g "$DEPLOY_USER" /home/$DEPLOY_USER/.ssh
touch /home/$DEPLOY_USER/.ssh/authorized_keys
cat /root/.ssh/authorized_keys >> /home/$DEPLOY_USER/.ssh/authorized_keys
[ -n "${CI_PUBKEY:-}" ] && echo "$CI_PUBKEY" >> /home/$DEPLOY_USER/.ssh/authorized_keys
sort -u -o /home/$DEPLOY_USER/.ssh/authorized_keys /home/$DEPLOY_USER/.ssh/authorized_keys
chown "$DEPLOY_USER:$DEPLOY_USER" /home/$DEPLOY_USER/.ssh/authorized_keys
chmod 600 /home/$DEPLOY_USER/.ssh/authorized_keys

# 3. Swap 4 GB
if ! swapon --show | grep -q /swapfile; then
  fallocate -l 4G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile
  grep -q '/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi
echo 'vm.swappiness=10' > /etc/sysctl.d/99-arw.conf && sysctl --system >/dev/null
timedatectl set-timezone UTC

# 4. Firewall
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp && ufw allow 80/tcp && ufw allow 443/tcp
ufw --force enable

# 5. fail2ban
cat > /etc/fail2ban/jail.d/sshd.local <<'J'
[sshd]
enabled = true
maxretry = 5
findtime = 10m
bantime = 1h
J
systemctl enable --now fail2ban && systemctl restart fail2ban

# 6. Unattended security upgrades (no automatic reboot)
cat > /etc/apt/apt.conf.d/20auto-upgrades <<'U'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
APT::Periodic::AutocleanInterval "7";
U
sed -i 's#^//\?\s*Unattended-Upgrade::Automatic-Reboot .*#Unattended-Upgrade::Automatic-Reboot "false";#' /etc/apt/apt.conf.d/50unattended-upgrades || true

# 7. Docker Engine + compose plugin (official repo)
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
. /etc/os-release
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu ${VERSION_CODENAME} stable" > /etc/apt/sources.list.d/docker.list
apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
cat > /etc/docker/daemon.json <<'D'
{ "log-driver": "json-file", "log-opts": { "max-size": "10m", "max-file": "3" }, "live-restore": true }
D
systemctl enable --now docker && systemctl restart docker
usermod -aG docker "$DEPLOY_USER"

# 8. App directory
install -d -m 750 -o "$DEPLOY_USER" -g "$DEPLOY_USER" "$APP_DIR" "$APP_DIR/backups" "$APP_DIR/caddy"
[ -f "$APP_DIR/.env" ] || install -m 600 -o "$DEPLOY_USER" -g "$DEPLOY_USER" /dev/null "$APP_DIR/.env"

# 9. Lock SSH down only if the deploy user has at least one key
if [ -s /home/$DEPLOY_USER/.ssh/authorized_keys ]; then
  cat > /etc/ssh/sshd_config.d/99-arw-hardening.conf <<'S'
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin no
PubkeyAuthentication yes
MaxAuthTries 3
X11Forwarding no
S
  sshd -t && systemctl restart ssh
else
  echo "Refusing to disable root/password login: /home/$DEPLOY_USER/.ssh/authorized_keys is empty" >&2; exit 1
fi
echo "bootstrap done: log in as $DEPLOY_USER with your key; root and passwords are now disabled"
```

Note on `NOPASSWD` sudo: it lets Cursor and the deploy job run maintenance without a password. The risk is bounded because only key holders can log in. To tighten later, replace it with a sudoers rule limited to `systemctl`, `ufw`, `apt-get`.

## 4. Docker + compose plugin

Installed by the script above from Docker's official apt repo (`docker-ce`, `docker-compose-plugin`, `docker-buildx-plugin`). Use `docker compose` (v2 plugin), never the old `docker-compose` binary. Check with `docker compose version` and `docker info | grep -i 'logging driver'`.

## 5. `docker-compose.prod.yml` design (Cursor creates the file at the repo root)

Images come from GHCR, tagged with the git SHA; the server never builds. All app containers share `env_file: /opt/arw-ml-lab/.env`.

| Service | Image / command | Restart | Memory limit (`mem_limit`) | CPU | Notes |
|---|---|---|---|---|---|
| `caddy` | `caddy:2-alpine`; mounts `infra/caddy/Caddyfile`, volumes `caddy_data`, `caddy_config` | `unless-stopped` | 128 MB | 0.25 | the **only** service with `ports: ["80:80","443:443"]` |
| `lab-api` | `ghcr.io/shibayanbiswas/arw-ml-lab-api:${IMAGE_TAG}`; `uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --workers 2 --proxy-headers --forwarded-allow-ips="*"` | `unless-stopped` | 1.0 GB | 1.0 | healthcheck `GET http://127.0.0.1:8000/healthz` every 15 s; `SERVICE_ROLE=api` |
| `worker-light` | `…-worker-light:${IMAGE_TAG}`; `celery -A backend.worker.celery_app worker -Q q.ingest,q.eda,q.insights,q.report,q.predict.batch --concurrency 2 --prefetch-multiplier 1 --max-tasks-per-child 20` | `unless-stopped` | 1.5 GB | 1.0 | `stop_grace_period: 300s`; `SERVICE_ROLE=worker-light` |
| `worker-train` | `…-worker-train:${IMAGE_TAG}`; same Celery command with `-Q q.train.cpu,q.tune,q.explain,q.forecast,q.predict.heavy --concurrency 1 --prefetch-multiplier 1 --max-tasks-per-child 10` | `unless-stopped` | 3.5 GB (`memswap_limit` 5 GB) | 2.0 | `stop_grace_period: 300s`; env `OMP_NUM_THREADS=2`, `MKL_NUM_THREADS=2`, `TORCH_NUM_THREADS=2`, `LAB_GPU_WORKER=false` |
| `lab-beat` | worker-light image; `sh -c 'while true; do python -m backend.worker.maintenance --all; sleep 3600; done'` | `unless-stopped` | 256 MB | 0.25 | replaces the Render cron job |
| `redis` | `redis:7-alpine`; `redis-server --requirepass $REDIS_PASSWORD --appendonly yes --maxmemory 512mb --maxmemory-policy noeviction` | `unless-stopped` | 640 MB | 0.5 | volume `redis_data:/data`; **no `ports:`**; healthcheck `redis-cli -a $REDIS_PASSWORD ping` |
| `mlflow` (profile `mlflow`, optional) | `ghcr.io/mlflow/mlflow:<pinned>`; backend store = Supabase Postgres schema `mlflow` (`DATABASE_URL_SESSION`), artefacts = Supabase S3 bucket `models/mlflow` | `unless-stopped` | 512 MB | 0.5 | internal only; reachable from workers at `http://mlflow:5000`; if enabled, lower `worker-train` to 3.0 GB |

Images (three GHCR packages from `backend/Dockerfile` with `REQUIREMENTS_LOCK` build arg, no Dockerfile logic change needed):
- `arw-ml-lab-api` ← `backend/requirements/api.lock.txt`
- `arw-ml-lab-worker-light` ← `backend/requirements/worker-light.lock.txt`
- `arw-ml-lab-worker-train` ← `backend/requirements/worker-train.lock.txt` (CPU torch; large image, ~3–5 GB; 75 GB disk is fine with `docker image prune` keeping 2 tags)

Shared settings: one bridge network `lab`; `depends_on: redis: condition: service_healthy`; `REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0`; `init: true` on workers; `logging` inherits daemon rotation; `IMAGE_TAG` read from `/opt/arw-ml-lab/.deploy.env`.

**Memory budget (8 GB RAM + 4 GB swap)**

| Component | Limit |
|---|---|
| Ubuntu + Docker daemon + sshd/fail2ban | ~0.7 GB (not limited) |
| caddy | 0.125 GB |
| redis | 0.625 GB (maxmemory 512 MB) |
| lab-api (2 uvicorn workers) | 1.0 GB |
| worker-light (concurrency 2) | 1.5 GB |
| worker-train (concurrency 1) | 3.5 GB |
| lab-beat | 0.25 GB |
| **Total (without mlflow)** | **~7.7 GB** |
| mlflow (optional) | +0.5 GB, take 0.5 GB from worker-train |

Limits are hard caps: a runaway training job is OOM-killed inside `worker-train` (Celery marks the task failed, `--max-tasks-per-child` recycles the process) instead of taking the API down. Swap is a safety net only; if `free -h` shows swap in steady use, move to the 6 vCPU / 12 GB tier (§12).

## 6. Caddy (HTTPS) and hostname (`infra/caddy/Caddyfile`, created by Cursor)

```caddyfile
{
  email {$ACME_EMAIL}
}
{$LAB_API_HOSTNAME} {
  encode zstd gzip
  request_body {
    max_size 60MB          # Prediction Studio uploads (LAB_PREDICT_MAX_MB=50); dataset uploads go straight to Supabase
  }
  reverse_proxy lab-api:8000 {
    flush_interval -1      # stream SSE job progress without buffering
    health_uri /healthz
  }
  header {
    Strict-Transport-Security "max-age=31536000"
    X-Content-Type-Options nosniff
    Referrer-Policy strict-origin-when-cross-origin
    -Server
  }
  log {
    output stdout
    format json
  }
}
```

Hostname choice:
- With a domain: `LAB_API_HOSTNAME=api.<domain>` (DNS `A` record → VPS IP, set before first start).
- Without a domain: `LAB_API_HOSTNAME=<a-b-c-d>.sslip.io` (IP with dashes; `nip.io` works the same). Let's Encrypt issues for it; it shares rate limits with other sslip.io users, so if issuance is rate-limited, retry later or use a domain.
- The browser calls this host from `https://arw-ml-lab.vercel.app`, so it **must** be HTTPS (mixed content otherwise).

## 7. Server env file `/opt/arw-ml-lab/.env`

Owner `deploy`, mode `600` (`chmod 600 /opt/arw-ml-lab/.env`), never in git, never printed in logs. Written by Cursor from the local `.env` over SSH (`scp` of a temp file, then `shred` the temp). This is the **only** place `NVIDIA_API_KEY` lives in production (never Vercel, never GitHub).

| Group | Variables |
|---|---|
| Runtime | `APP_ENV=production`, `LAB_DEFAULT_SEED=42`, `AUTH_MODE=bff`, `JWT_SECRET` (same value as Vercel), `AUTH_TEST_BYPASS=false`, `LAB_DEFAULT_WORKSPACE_ID` |
| Network | `LAB_API_HOSTNAME`, `ACME_EMAIL`, `CORS_ALLOWED_ORIGINS=https://arw-ml-lab.vercel.app` (comma-separate a custom frontend domain if added; no `*`) |
| Redis | `REDIS_PASSWORD` (32+ random chars), `REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0` |
| Supabase | `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_JWKS_URL`, `DATABASE_URL` (transaction pooler), `DATABASE_URL_SESSION` (session pooler), `SUPABASE_S3_ENDPOINT`, `SUPABASE_S3_REGION`, `SUPABASE_S3_ACCESS_KEY_ID`, `SUPABASE_S3_SECRET_ACCESS_KEY` |
| AI (§40) | `AI_ENABLED=true`, `AI_PROVIDER_PRIMARY=nvidia`, `AI_BASE_URL=https://integrate.api.nvidia.com/v1`, `NVIDIA_API_KEY`, optional `GEMINI_API_KEY`/`OPENROUTER_API_KEY`/`GROQ_API_KEY`, `AI_RPM_LIMIT=35`, `AI_DAILY_REQUEST_CAP=500`, `AI_USER_DAILY_REQUEST_CAP=150`, `AI_IMAGE_MAX_B64_BYTES=170000` |
| Limits | `LAB_MAX_ROWS=2000000`, `LAB_JOB_SOFT_LIMIT_TRAIN_MIN=90`, `LAB_JOB_HARD_LIMIT_TRAIN_MIN=120`, `LAB_PREDICT_MAX_MB=50`, `LAB_PREDICT_MAX_ROWS=1000000`, `LAB_PREDICT_CHUNK_ROWS=50000`, `LAB_PREDICT_RETENTION_DAYS=30`, `STORAGE_BUCKET_PREDICTIONS=predictions`, `TABPFN_ENABLED=false`, `LAB_GPU_WORKER=false` |
| Optuna | `OPTUNA_STORAGE_URL` = Postgres session URL (`DATABASE_URL_SESSION` style) so tune studies resume after worker restart (§39.3) |
| Observability | `SENTRY_DSN`, `SENTRY_ENVIRONMENT=production`, optional `HEALTHCHECK_PING_URL` (lab-beat → healthchecks.io after maintenance) |
| MLflow (optional) | `MLFLOW_TRACKING_URI=http://mlflow:5000` only when the profile is on |

`/opt/arw-ml-lab/.deploy.env` (written by the deploy job, not secret): `IMAGE_TAG=<sha>`, `PREV_IMAGE_TAG=<sha>`, `GHCR_OWNER=shibayanbiswas`.

## 8. CI/CD: GitHub Actions → GHCR → SSH deploy (Cursor rewrites `deploy.yml`)

Trigger stays `workflow_run` of CI on `main` + `workflow_dispatch`. Jobs:

1. **`migrate`** — unchanged (Supabase CLI `link` + `db push`; strict secret guard). Migrations always run before new code starts (expand → migrate → contract, ST-OPS-04).
2. **`build`** (parallel with migrate) — `permissions: { contents: read, packages: write }`; `docker/setup-buildx-action`, `docker/login-action` to `ghcr.io` with `GITHUB_TOKEN`; matrix `{api, worker-light, worker-train}` → `docker/build-push-action` with `file: backend/Dockerfile`, `build-args: REQUIREMENTS_LOCK=…`, tags `ghcr.io/<owner>/arw-ml-lab-<svc>:${{ github.sha }}` and `:main`, `cache-from/to: type=gha,scope=<svc>`.
3. **`deploy`** — `needs: [migrate, build]`, `environment: production`, `concurrency: { group: deploy-prod, cancel-in-progress: false }`, `permissions: { packages: read }`. Steps:
   - write `CONTABO_SSH_KEY` to `~/.ssh/id_ed25519` (600) and `CONTABO_KNOWN_HOSTS` to `~/.ssh/known_hosts` (`StrictHostKeyChecking yes`; never `ssh-keyscan` inside CI);
   - `scp docker-compose.prod.yml infra/caddy/Caddyfile infra/contabo/deploy.sh scripts/backup_contabo.sh` → `/opt/arw-ml-lab/` (compose + Caddyfile + `deploy.sh` + nightly backup script);
   - `ssh deploy@$CONTABO_HOST` and run `deploy.sh <sha>` with the GHCR token piped on stdin (`echo "$GITHUB_TOKEN" | docker login ghcr.io -u $GITHUB_ACTOR --password-stdin`; the token expires with the job, no long-lived registry secret on the server).
4. **`smoke`** — `curl -fsS "$LAB_API_URL/healthz"` (30 × 10 s) from the runner over the public HTTPS hostname; optional DS1 EDA via `scripts/smoke_hosted.sh` when `vars.SMOKE_EDA == 'true'`.

`/opt/arw-ml-lab/deploy.sh` (Cursor creates it under `infra/contabo/deploy.sh` and copies it to the server):

```bash
#!/usr/bin/env bash
# deploy.sh <new_tag>: pull, start, health-check, roll back on failure.
set -euo pipefail
cd /opt/arw-ml-lab
NEW="$1"; touch .deploy.env
PREV="$(grep -E '^IMAGE_TAG=' .deploy.env | cut -d= -f2 || true)"
C="docker compose --env-file .env --env-file .deploy.env -f docker-compose.prod.yml"
printf 'IMAGE_TAG=%s\nPREV_IMAGE_TAG=%s\nGHCR_OWNER=shibayanbiswas\n' "$NEW" "$PREV" > .deploy.env
$C pull --quiet
$C up -d --remove-orphans
for i in $(seq 1 30); do
  if $C exec -T lab-api python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/healthz',timeout=3).status==200 else 1)"; then
    echo "healthy: $NEW"; docker image prune -af --filter "until=168h" >/dev/null || true; exit 0
  fi
  sleep 5
done
echo "UNHEALTHY: rolling back to ${PREV:-<none>}" >&2
$C logs --tail 200 lab-api >&2 || true
if [ -n "$PREV" ]; then
  printf 'IMAGE_TAG=%s\nPREV_IMAGE_TAG=%s\nGHCR_OWNER=shibayanbiswas\n' "$PREV" "$PREV" > .deploy.env
  $C up -d --remove-orphans
fi
exit 1
```

Manual rollback: `ssh deploy@host 'cd /opt/arw-ml-lab && ./deploy.sh <older_sha>'` (any SHA still in GHCR). Workers finish their current task on stop (300 s grace); long Optuna studies resume (§39.13 AC 6).

## 9. Secrets, variables, Vercel env, CORS

GitHub → Settings → Environments → `production` (set by Cursor with `gh secret set … --env production`, values piped from files, never echoed):

| Name | Kind | Value |
|---|---|---|
| `SUPABASE_ACCESS_TOKEN` | secret | personal access token from `supabase login` / dashboard |
| `SUPABASE_PROJECT_ID` | secret | `ushtfpelbpjfkjoppklz` |
| `SUPABASE_DB_PASSWORD` | secret | database password |
| `CONTABO_HOST` | secret | VPS IP (or hostname) |
| `CONTABO_USER` | secret | `deploy` |
| `CONTABO_SSH_KEY` | secret | **CI-only** private key (`ssh-keygen -t ed25519 -f arw_ci_deploy -N ""`), public half in `deploy`'s `authorized_keys`; separate from your personal key so it can be revoked alone |
| `CONTABO_KNOWN_HOSTS` | secret | output of `ssh-keyscan -t ed25519 <host>`, verified once against `ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub` on the server |
| `LAB_API_URL` | variable | `https://<LAB_API_HOSTNAME>` |
| `SMOKE_EDA` | variable | `false` (set `true` only on staging with `AUTH_TEST_BYPASS`) |

Legacy (Render path only, leave unset): `RENDER_DEPLOY_HOOK_API`, `RENDER_DEPLOY_HOOK_WORKER_LIGHT`, `RENDER_DEPLOY_HOOK_WORKER_TRAIN`.

Vercel project `arw-ml-lab` (Production + Preview): `NEXT_PUBLIC_LAB_API_URL=https://<LAB_API_HOSTNAME>` (rebuild required because it is inlined at build time), `JWT_SECRET` identical to the server. `NVIDIA_API_KEY` is **never** added to Vercel (CI grep test stays).

CORS: `CORS_ALLOWED_ORIGINS=https://arw-ml-lab.vercel.app` on the server; preview deployments call the API only if you add their exact origin. Credentials travel as `Authorization: Bearer` (no cross-site cookies), so no `*`.

## 10. Backups

| What | How | Retention |
|---|---|---|
| Postgres, Auth | Supabase (daily backups on Pro; PITR optional) | per Supabase plan |
| Supabase Storage `models/` and `datasets/` buckets | nightly `rclone sync` from the private `backups` bucket prefix (service-role S3 credentials in `.env`); objects are **not** in DB backups | 30 days off-site |
| Redis volume (queue state, Optuna progress cache) | host cron `03:30 UTC` runs `scripts/backup_contabo.sh` (BGSAVE + `redis-*.tgz` of the `redis_data` volume) | 7 days local |
| MLflow volume / config (if enabled) | same cron, `mlflow-$(date +%F).tgz` | 7 days local |
| `/opt/arw-ml-lab/.env`, Caddyfile, compose file | `tar` with `.env` encrypted (`age` or `gpg --symmetric`) | 7 days local |
| Off-site copy | `rclone copy /opt/arw-ml-lab/backups supabase-s3:backups/contabo/` (private bucket `backups`) or Contabo Object Storage | 30 days |
| Whole server | Contabo **snapshot** from the Customer Control Panel before risky changes (OS upgrade, compose redesign); the plan includes 1–2 snapshot slots, older snapshots auto-expire | keep latest |

Restore drill (once, then quarterly): fresh VPS → bootstrap → copy `.env` → `deploy.sh <last_good_sha>` → restore redis volume → `/healthz` 200.

## 11. Monitoring and logs

- **Uptime**: an external monitor on `https://<LAB_API_HOSTNAME>/healthz` every 1 min (healthchecks.io, UptimeRobot free, or **Uptime Kuma** run *outside* this VPS so it can see the VPS being down). Alert by email.
- **Heartbeat**: `lab-beat` pings a healthchecks.io URL (env `HEALTHCHECK_PING_URL`, optional) after each hourly maintenance run.
- **Errors**: Sentry (`SENTRY_DSN` on server, `NEXT_PUBLIC_SENTRY_DSN` on Vercel).
- **Logs**: `docker compose logs -f --tail 200 <svc>`; rotation via `daemon.json` (10 MB × 3 per container). Caddy logs JSON to stdout.
- **Resources**: `docker stats --no-stream`, `free -h`, `df -h /`; alert manually if disk > 80 % (`docker image prune -af --filter until=168h`).
- **Egress (optional, OPS-14)**: on the host, `python scripts/render_egress_nft.py` prints an nftables drop-by-default snippet with `# ALLOW_HOST` lines from `data/samples/urls.txt` + NVIDIA/Supabase; resolve IPs then `nft -f` only after review (never apply blindly).

## 12. Operations

**Restart policy**: every service `restart: unless-stopped`; Docker starts on boot; `live-restore: true` keeps containers up through a daemon restart. After a kernel update: `sudo reboot` in a quiet window, then check `/healthz`.

**Cost (Nov 2026, re-check before buying)**: Cloud VPS 10 / 4 vCPU 8 GB about EUR 4.50–6.60 per month incl. location fee; Vercel Hobby/Pro unchanged; Supabase Pro (needed for > 50 MB uploads). Compared with the Render plan in §39.3 (web + 2 workers + key value + cron), this is a large saving, traded for self-managed ops.

**Limits on this box (no GPU)**

| Area | Limit / default |
|---|---|
| GPU models (xLSTM, large TabPFN, GPU-only DL) | refused with HTTP 422 (`LAB_GPU_WORKER=false`, existing guard) |
| Deep learning | CPU only; Quick/Balanced presets, small epochs, batch ≤ 256, `TORCH_NUM_THREADS=2` |
| TabPFN | off (`TABPFN_ENABLED=false`) |
| Concurrent heavy jobs | 1 training/tuning job at a time (queue waits); 2 light jobs |
| Thorough / Exhaustive tuning, large CPCV | allowed but slow; prefer Balanced; hard limit 120 min |
| Dataset rows | `LAB_MAX_ROWS=2000000` (raise only after load tests) |
| Batch prediction | 1M rows in 50k chunks on `q.predict.batch` / `q.predict.heavy` |
| Upload through API | ≤ 60 MB (Caddy); datasets go browser → Supabase directly |
| Scale-up path | Contabo 6 vCPU / 12 GB tier (in-place upgrade), or a second VPS running only `worker-train` against the same Redis over a WireGuard tunnel |

**Troubleshooting**

| Symptom | Check / fix |
|---|---|
| `ssh: Permission denied (publickey)` | right key? `ssh -i <key> -v deploy@host`; root login is off by design; use Contabo VNC console to recover |
| Caddy cannot get a certificate | DNS A record points at the VPS? ports 80/443 open in ufw? `docker compose logs caddy`; sslip.io rate-limited → use a domain |
| Browser CORS error | `CORS_ALLOWED_ORIGINS` exact origin, no trailing slash; restart `lab-api` |
| Mixed content / API calls blocked | `NEXT_PUBLIC_LAB_API_URL` must be `https://`; redeploy Vercel after changing it |
| 401 from API | `JWT_SECRET` differs between Vercel and server; `AUTH_MODE=bff` |
| Jobs stay queued | `docker compose ps`; worker logs; `REDIS_URL` password; queue names match the router |
| Worker restarts with exit 137 | OOM: lower preset / rows, or raise tier; check `docker inspect --format '{{.State.OOMKilled}}'` |
| Deploy job fails at SSH | `CONTABO_KNOWN_HOSTS` stale after rebuild/reinstall → refresh and verify fingerprint |
| Deploy rolled back | read the printed `lab-api` logs; fix; push again |
| Disk full | `docker system df`; prune old images; check backups folder |

## 13. Acceptance criteria (Contabo path; replaces §39.13 AC 1 for the backend)

1. `ssh root@host` fails; `ssh deploy@host` works only with a key; `ufw status` shows 22/80/443 only; `fail2ban-client status sshd` active; `swapon --show` shows 4 GB.
2. `docker compose -f docker-compose.prod.yml ps` shows caddy, lab-api, worker-light, worker-train, lab-beat, redis healthy/running; `redis` has no published port (`ss -tlnp | grep 6379` empty on the host).
3. `curl -fsS https://<LAB_API_HOSTNAME>/healthz` returns 200 with a valid Let's Encrypt certificate.
4. Deploy workflow green: migrate → build → deploy → smoke; a deliberately broken image is rolled back to the previous tag automatically.
5. From `https://arw-ml-lab.vercel.app`, sign in and run the DS1 sample EDA end to end; artefacts appear in Supabase Storage; progress streams over SSE through Caddy.
6. `NVIDIA_API_KEY` exists only in `/opt/arw-ml-lab/.env` (600); absent from Vercel, GitHub and client bundles.
7. A nightly backup file exists and one restore drill is recorded in `docs/PROGRESS.md`.
