# Phase 2 — Auth/brand + thin supervised slice

Approved plan: `phase_2_auth_thin_542562df`.

## Locked decisions

1. BFF auth (SP password + on-screen OTP + Rathi roster); no Supabase email/magic OTP. Users in Postgres (not Mongo). ADR-0005.
2. Product name: Machine Learning Lab; ARWL logo from SP brand assets.
3. Thin ML: recipe + ≥10 algorithms + KFold/Stratified CV + leaderboard on DS3/DS12. Full §41/§42 and remaining R*/C* → Phase 2-cont.
4. Free hosting: Vercel Hobby + existing Supabase; Render only if free without payment — else local API.

## Workstreams

0. Auth/brand/deploy  
1. Preprocess + train + leaderboard  
2. Tests, report, commit, STOP
