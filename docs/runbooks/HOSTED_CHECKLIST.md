# Hosted checklist — paste into chat when each step is done (no secrets)

Use this after following [docs/DEPLOY.md](../DEPLOY.md). Reply with ticks only; never paste keys.

## Supabase

- [x] Project created (region: `ap-south-1`, ref `ushtfpelbpjfkjoppklz`)
- [ ] Global file size limit ≥ 2 GB (Pro + Storage settings)
- [x] Migrations applied (MCP apply; buckets + RLS present)
- [ ] Auth redirect URLs include Vercel domains (`https://arw-ml-lab.vercel.app/auth/callback`)
- [x] Project ref (non-secret): `ushtfpelbpjfkjoppklz`

## Render

- [x] Blueprint created (`exs-dbsnkbpsrm7s73drvi90`) — **approve blocked** until payment method
- [ ] Blueprint applied; services listed: lab-api, lab-worker-light, lab-worker-train, lab-beat, lab-kv
- [ ] `lab-shared` secrets filled (`sync: false` keys)
- [ ] Deploy hooks copied to GitHub Environment secrets
- [ ] lab-api public URL: ________

## Vercel

- [x] Project linked; Root Directory = `frontend`
- [x] Only `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `NEXT_PUBLIC_LAB_API_URL` set
- [x] Production URL: `https://arw-ml-lab.vercel.app`
- [ ] Update `NEXT_PUBLIC_LAB_API_URL` once lab-api exists

## GitHub

- [x] Environment `production` created
- [ ] Environment secrets/vars set (after Render hooks + Supabase tokens)
- [ ] Branch protection on `main` requires CI (**needs GitHub Pro** on private repo)
- [ ] Actions → Deploy smoke: healthz green
