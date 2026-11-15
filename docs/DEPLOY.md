# Deploy guide — ARW ML Lab (ARCHITECTURE §39)

Phase 8.1 hosted skeleton. Secrets never go in git or chat; set them in the vendor dashboards and GitHub Environment `production`.

## Topology

| Piece | Platform | Notes |
|---|---|---|
| UI | **Vercel** | Root Directory = `frontend`; region `sin1` |
| API + SSE | **Render** `lab-api` | FastAPI; JWT from Supabase JWKS |
| Light jobs | **Render** `lab-worker-light` | `q.ingest`, `q.eda`, … |
| Train jobs | **Render** `lab-worker-train` | `q.train.cpu`, `q.tune`, … (later phases) |
| Hourly cron | **Render** `lab-beat` | `python -m backend.worker.maintenance --all` |
| Broker | **Render** `lab-kv` | Key Value, `noeviction`, internal |
| DB / Auth / Storage | **Supabase** | Pro; Mumbai `ap-south-1` or Singapore |

Uploads: browser → Supabase Storage signed URL (not through Vercel). SSE: browser → `lab-api` directly (CORS allow-list).

## Plans (re-check pricing before buy)

| Service | Plan in `render.yaml` |
|---|---|
| lab-api | `1c-2g` |
| lab-worker-light | `2c-4g` |
| lab-worker-train | `4c-16g` |
| lab-beat | `0.5c-512mb` cron |
| lab-kv | `1g`, `noeviction` |
| Supabase | **Pro** (raise global file size limit to **2 GB**) |
| Vercel | Pro recommended for company use |

## One-time setup (order)

### 1. GitHub

1. Private repo `arw-ml-lab` on `main` (CI/deploy listen on `main`).
2. Branch protection: require CI status checks before merge.
3. Environment **production** with secrets/vars (below).

### 2. Supabase

1. Create Pro project (Mumbai or Singapore).
2. Dashboard → Storage: set project global file size limit ≥ 2 GB.
3. Auth → URL configuration: add Vercel production + preview redirect URLs.
4. Auth → (optional) restrict sign-in to company email domains.
5. Copy project URL, anon key, service role key, JWKS URL, pooler connection strings.
6. Link + push migrations:

```bash
supabase login
supabase link --project-ref <PROJECT_REF>
supabase db push --remote --yes
```

Buckets `datasets`, `artefacts`, `models`, `reports`, `plots`, `predictions` and RLS come from kit migrations.

### 3. Render

1. New Blueprint from repo `render.yaml` (Singapore).
2. Confirm services: `lab-api`, `lab-worker-light`, `lab-worker-train`, `lab-beat`, `lab-kv`.
3. Env group `lab-shared`: fill every `sync: false` key (see matrix).
4. Set `CORS_ALLOWED_ORIGINS` to the Vercel production (+ preview) origins.
5. Leave `autoDeployTrigger: off`; copy **Deploy Hook** URLs for api + both workers into GitHub secrets.
6. Optional: leave `NVIDIA_API_KEY` empty → numbers-only AI until set.

### 4. Vercel

1. Import repo; **Root Directory** = `frontend`.
2. Env (Production + Preview):

| Variable | Value |
|---|---|
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | publishable/anon key only |
| `NEXT_PUBLIC_LAB_API_URL` | `https://<lab-api>.onrender.com` |

**Never** set `NVIDIA_API_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, or any `DATABASE_URL` on Vercel.

### 5. GitHub Environment `production`

**Secrets**

| Name | Source |
|---|---|
| `SUPABASE_ACCESS_TOKEN` | supabase.com account token |
| `SUPABASE_DB_PASSWORD` | project DB password |
| `SUPABASE_PROJECT_ID` | project ref |
| `RENDER_DEPLOY_HOOK_API` | Render deploy hook |
| `RENDER_DEPLOY_HOOK_WORKER_LIGHT` | Render deploy hook |
| `RENDER_DEPLOY_HOOK_WORKER_TRAIN` | Render deploy hook |

**Variables**

| Name | Value |
|---|---|
| `LAB_API_URL` | public `lab-api` base URL (no trailing slash) |
| `SMOKE_EDA` | `true` only on a staging stack that allows `AUTH_TEST_BYPASS` |

## Deploy flow

1. Push/PR to `main` → `ci.yml` (frontend, backend, kit-checks, supabase).
2. On CI success → `deploy.yml`: migrations → Render hooks → healthz smoke.
3. Vercel deploys via Git integration independently.

Manual: Actions → Deploy → Run workflow.

## Smoke tests

```bash
# Health only
curl -fsS "$LAB_API_URL/healthz"

# Full DS1 EDA (requires AUTH_TEST_BYPASS=true on that API — staging only)
LAB_API_URL=https://… bash scripts/smoke_hosted.sh
```

Local without Docker Supabase CLI: `uv run python tests/db_harness/run_db_tests.py`.

## Rollback

1. **App:** Render → previous successful deploy for `lab-api` / workers; Vercel → promote prior deployment.
2. **DB:** prefer expand → migrate → contract (OPS-11). Do not rewrite applied migrations; add a reverse migration. PITR restore to a scratch project for drills (Phase 8.2).
3. **Disable traffic:** scale Render services to 0 / pause; keep Supabase for data.

## Security checklist

- [ ] Service role + `NVIDIA_API_KEY` only on Render (and local `.env`).
- [ ] Anon key only in Vercel `NEXT_PUBLIC_*`.
- [ ] CI grep fails if secrets appear in `.next/static`.
- [ ] RLS covered by `supabase test db` / db_harness.
- [ ] `AUTH_TEST_BYPASS` and `LAB_AUTH_BYPASS` never `true` in production.

## Phase 8.1 vs later

| Item | When |
|---|---|
| healthz + DS1 EDA smoke | 8.1 |
| Full DS1 train → explain → predict | Phase 2+ then re-check §39.13 |
| Optuna resume, heartbeats reaper, PITR drill | Phase 8.2 |
| TradingLab submodule | Phase 5 |
