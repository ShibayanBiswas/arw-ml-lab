# ADR (proposed number ADR-0015): Backend moves from Render to a Contabo Cloud VPS

- Status: Accepted (16 Nov 2026, IST)
- Deciders: Shibayan Biswas
- Supersedes: the Render backend part of §39 / ADR-0003 hosting notes. Vercel (frontend) and Supabase (Postgres, Auth, Storage) are unchanged.
- Append this text to `docs/DECISIONS.md` as the next ADR number (ADR-0015 if 0014 is the latest).

## Context
- The Render Blueprint (`exs-dbsnkbpsrm7s73drvi90`) never provisioned. Every service failed with `need_payment_info`, so there is no live `lab-api`.
- The Deploy workflow's `render` and `smoke` jobs cannot pass. The `migrate` job fails separately because the Supabase GitHub secrets are missing.
- The Render plan sized in §39.3 is a recurring cost many times higher than a single VPS:
  - web 1c-2g;
  - workers 2c-4g and 4c-16g;
  - key value 1g;
  - cron.
- The workload is a small internal team: one heavy training job at a time is acceptable.
- There is no GPU requirement on the hosted path. GPU-only models already refuse with HTTP 422.

## Decision
- Run the whole backend on one **Contabo Cloud VPS 10**: 4 vCPU, 8 GB RAM, 75 GB NVMe, Ubuntu 24.04, region Mumbai or else Singapore. The backend is:
  - `lab-api`, `worker-light`, `worker-train` and `lab-beat`;
  - Redis;
  - optional MLflow.
- Use Docker Compose (`docker-compose.prod.yml`) behind Caddy with automatic Let's Encrypt HTTPS.
- Images are built in GitHub Actions and pushed to GHCR. They are deployed over SSH with a health check and automatic rollback to the previous tag.
- Supabase migrations stay in the `migrate` job and always run first.
- `NVIDIA_API_KEY` and all backend secrets live only in `/opt/arw-ml-lab/.env` (mode 600).
- `render.yaml` stays in the repo as the **alternative / legacy** path and is not deleted.
- The runbook is `docs/DEPLOY_CONTABO.md`.

## Consequences
- Positive:
  - Cost of about EUR 5–7/month for the backend.
  - The deploy is unblocked without a Render payment method.
  - Full control (SSH, logs, limits).
  - Same images run locally and in production.
- Negative:
  - Self-managed security patching, backups and monitoring (covered in the runbook §3, §10, §11).
  - A single host is a single point of failure, mitigated by Contabo snapshots, the restore drill and Supabase holding all durable data.
  - 8 GB RAM caps concurrency: memory limits per container, one training job at a time, small DL defaults.
- Neutral: the code does not change. The same `backend/Dockerfile` is used with the `REQUIREMENTS_LOCK` build argument. Only `deploy.yml`, the compose file, the Caddyfile and the docs are added or changed.

## Alternatives considered
1. Pay for Render (original §39 plan). Simplest operations, highest cost; kept as the legacy path.
2. Fly.io, Railway or Hetzner. These are viable. Contabo was chosen for price per GB of RAM and its Mumbai region.
3. Kubernetes (§39.12). Overkill at this scale; it remains the long-term scale-out option for workers.

## Revisit when
- More than one heavy job must run at once.
- Swap is in steady use.
- GPU training is needed.

In those cases, upgrade the tier, add a second worker-train VPS, or move workers to Kubernetes.
