# ARW ML Lab — One-shot finish report (interim)

**Date:** 16 Nov 2026 (IST)  
**Tip:** oneshot-c17 (GARCH; c16 green `abe28cc`)  
**Live frontend:** https://arw-ml-lab.vercel.app/login → **200**  
**Repo:** https://github.com/ShibayanBiswas/arw-ml-lab

Honest interim closeout. Chunk A + deep B/C slices shipped with repeated **CI green**. Full AC closure for 4A→8.2 and every STRESS_TEST item is **not** done. Hosted Deploy remains blocked on secrets/Render payment.

## Per-phase status

| Phase | Status | Evidence |
|---|---|---|
| 0–2B, 8.1 thin | done | `docs/PHASE_*_REPORT.md` |
| 2 deepen | partial | expanded registry (~84), Halving + NSGA-II/Hyperband |
| 2A deepen | partial | train-window-only scaler; DeepWorkbench |
| 3 deepen | partial | ExplainWorkbench, TreeSHAP, permutation, LIME, DiCE, ALE |
| 3A deepen | partial | PV02/03/10/14/15, Celery batch ≤1M, cancel |
| 4 deepen | partial | + AutoARIMA/Naive/SeasonalWindowAverage |
| 4A | partial | metrics/models expand — not full F*/TS.P.* |
| 5B | partial | FS1–FS6, FS8, FS14–15, FS19–20; FS7/9–13/16–18 deferred |
| 5 | partial | purged/CPCV + PBO in-lab |
| 5A | partial | WFO planner + Ridge OOS retune loop |
| 6 | partial | unsupervised API/UI + mock AI insights |
| 6A | partial | deterministic VLM guards |
| 6B | not started | |
| 7 | partial | reports/drift/UI + httpx e2e smoke + Locust skeleton |
| 8.2 | partial | maintenance reaper/retention |

## One-shot commits

| Commit | Summary |
|---|---|
| 6851ce9 | Deploy RENDER_ENABLED gate, checkout@v5 |
| 5e7db5c…8dcd625 | B.1–B.3 PV/purged/Celery/TS |
| 8524aa6…dbcb069 | C.1–C.3 PBO/AI/guards |
| f63eb59 | interim FINAL + FS14/20 |
| 566c6ef…5ba9e44 | C.4–C.6 WFO/reports/drift |
| 666a2ba…3109058 | C.7–C.8 Experiments/Admin UI |
| 17e4ccc…c2390a5 | C.9–C.10 Halving + NSGA-II/Hyperband |
| 6fd12fa | C.11 Friedman–Nemenyi CD diagram |
| a4d7e55 | C.12 LIME + DiCE explain |
| 27cf517 | C.13 ALE + AutoARIMA/Naive/SWA |
| 62da077 | C.14 FS6/8/15/19 (CI format fail → fixed c15) |
| 6aef99b | C.15 e2e httpx + Locust skeleton |
| (c16) | C.16 WFO Ridge retune loop |

## CI / Deploy / Vercel

| System | Status | Notes |
|---|---|---|
| CI | green through c15 (`6aef99b`) | https://github.com/ShibayanBiswas/arw-ml-lab/actions/runs/43817898315 |
| Deploy migrate | **fails** | missing `SUPABASE_ACCESS_TOKEN` / `SUPABASE_DB_PASSWORD` |
| Deploy render/smoke | skipped honestly | until `RENDER_ENABLED=true` + migrate secrets |
| Vercel | READY / **200** | https://arw-ml-lab.vercel.app |

## Blocked — needs Shibayan

1. `gh secret set SUPABASE_ACCESS_TOKEN --env production --repo ShibayanBiswas/arw-ml-lab`
2. `gh secret set SUPABASE_DB_PASSWORD --env production --repo ShibayanBiswas/arw-ml-lab`
3. Pay/approve Render Blueprint → `vars.RENDER_ENABLED=true`, `vars.LAB_API_URL`, deploy-hook secrets, Vercel `NEXT_PUBLIC_LAB_API_URL`
4. `NVIDIA_API_KEY` in Render `lab-shared` only
5. Vendor `vendor/tradinglab` for FS6–19 + AFML parity
6. Optional: GitHub Pro branch protection; Supabase Storage 2 GB

## STRESS_TEST

Most items still open. Closed/partial: deploy honesty, PV deepen, DL leakage scaler, import allowlist (`umap`→`umap-learn`), maintenance reaper, KS drift.

## Next

Continue agent work on full 4A catalogue, TradingLab contracts, WFO retune, Playwright/Locust, §39.13 AC — then replace this interim FINAL_REPORT.
