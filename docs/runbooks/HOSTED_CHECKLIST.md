# Hosted checklist — paste into chat when each step is done (no secrets)

Use this after following [docs/DEPLOY.md](../DEPLOY.md). Reply with ticks only; never paste keys.

## Supabase

- [x] Project created (region: `ap-south-1`, ref `ushtfpelbpjfkjoppklz`)
- [ ] Global file size limit ≥ 2 GB (Pro + Storage settings)
- [x] Migrations applied (MCP apply; buckets + RLS present)
- [x] BFF auth tables migration `20261115180000_lab_bff_auth.sql` (lab_app_users / lab_otps) — Postgres only; **no** Supabase email OTP for primary login (ADR-0005)
- [ ] ~~Auth redirect URLs for magic link~~ — N/A while BFF cookies are primary
- [x] Project ref (non-secret): `ushtfpelbpjfkjoppklz`

## Render (free path)

- [x] Blueprint created (`exs-dbsnkbpsrm7s73drvi90`) — **approve blocked** `need_payment_info`
- [ ] Blueprint applied; services listed: lab-api, lab-worker-light, lab-worker-train, lab-beat, lab-kv
- [ ] `lab-shared` secrets filled (`sync: false` keys) — include `AUTH_MODE=bff`, `JWT_SECRET` matching Vercel
- [ ] Deploy hooks copied to GitHub Environment secrets
- [ ] lab-api public URL: ________
- [x] **Until payment OK:** use local/`docker compose` for `lab-api` + workers; Vercel frontend alone is fine for UI smoke

## Vercel

- [x] Project linked; Root Directory = `frontend`; display name **Machine Learning Lab**
- [x] Supabase `NEXT_PUBLIC_*` set; add `JWT_SECRET`, `NEXT_PUBLIC_APP_URL`, `SEED_DEFAULT_PASSWORD_MAP` (server-only) for BFF
- [x] Production URL: `https://arw-ml-lab.vercel.app`
- [ ] MCP team re-auth when SSO expires (approve consent link from agent); then inspect failed deploys
- [ ] Update `NEXT_PUBLIC_LAB_API_URL` once lab-api exists (or point at local tunnel for demos)

## GitHub

- [x] Environment `production` created
- [ ] Environment secrets/vars set (after Render hooks + Supabase tokens)
- [ ] Branch protection on `main` requires CI (**needs GitHub Pro** on private repo)
- [ ] Actions → Deploy smoke: healthz green
