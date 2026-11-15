# Hosted checklist — paste into chat when each step is done (no secrets)

Use this after following [docs/DEPLOY.md](../DEPLOY.md). Reply with ticks only; never paste keys.

## Supabase

- [ ] Pro project created (region: ________)
- [ ] Global file size limit ≥ 2 GB
- [ ] `supabase link` + `db push` succeeded
- [ ] Auth redirect URLs include Vercel domains
- [ ] Project ref (non-secret): ________

## Render

- [ ] Blueprint applied; services listed: lab-api, lab-worker-light, lab-worker-train, lab-beat, lab-kv
- [ ] `lab-shared` secrets filled (`sync: false` keys)
- [ ] Deploy hooks copied to GitHub Environment secrets
- [ ] lab-api public URL: ________

## Vercel

- [ ] Project linked; Root Directory = `frontend`
- [ ] Only `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `NEXT_PUBLIC_LAB_API_URL` set
- [ ] Production URL: ________

## GitHub

- [ ] Environment `production` secrets/vars set
- [ ] Branch protection on `main` requires CI
- [ ] Actions → Deploy smoke: healthz green
