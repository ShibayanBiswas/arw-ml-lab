# ARW ML Lab — One-shot finish report (interim)

**Date:** 16 Nov 2026 (IST)  
**Tip:** `aface40` (c38 FS11; prior c37 CI https://github.com/ShibayanBiswas/arw-ml-lab/actions/runs/43839812689)  
**Live frontend:** https://arw-ml-lab.vercel.app/login → **200**  
**Repo:** https://github.com/ShibayanBiswas/arw-ml-lab

Honest interim closeout. Chunk A + deep B/C slices shipped with repeated **CI green**. Full AC closure for 4A→8.2 and every STRESS_TEST item is **not** done. Hosted Deploy remains blocked on secrets/Render payment.

## Per-phase status

| Phase | Status | Evidence |
|---|---|---|
| 0–2B, 8.1 thin | done | `docs/PHASE_*_REPORT.md` |
| 2 deepen | partial | registry (~84), Halving/NSGA-II/Hyperband, CLE.P deepen |
| 2A deepen | partial | train-window-only scaler; DeepWorkbench |
| 3 deepen | partial | LIME/DiCE/ALE/EBM + **ONNX/skops**; Anchors off (BSL) |
| 3A deepen | partial | PV02/03/10/14/15, Celery batch ≤1M, cancel |
| 4 deepen | partial | AutoARIMA/Naive/SWA/GARCH + F3/F6/F7/F14/F15/F20/F25 |
| 4A | partial | metrics/models expand — not full F*/TS.P.* |
| 5B | partial | FS1–FS11, FS14–15, FS19–20; FS12–13/16–18 deferred |
| 5 | partial | purged/CPCV + PBO in-lab |
| 5A | partial | WFO planner + Ridge OOS retune loop |
| 6 | partial | unsupervised API/UI + mock AI + k-sweep/Shepard/ANO hist |
| 6A | partial | deterministic VLM guards |
| 6B | partial | CLU.P.K_SWEEP, DR trustworthiness + Shepard, ANO.P.SCORE_HIST, REE.P expand |
| 7 | partial | reports/drift/UI + httpx e2e + Locust + ZAP + Playwright/axe opt-in |
| 8.2 | partial | maintenance reaper/retention |

## Recent commits (c28+)

| Commit | Summary |
|---|---|
| 95c0e62 | C.28 preprocess pipeline-graph API |
| 6ad7cd7…b184167 | C.29 ONNX/skops + mypy fixes |
| 3c4b02e | C.30 F* + FS7/FS9 |
| 2ea77d7 | C.31 Playwright/axe opt-in |
| 2cd4563 | C.32 CLE.P learning/validation |
| 8ab5d2d | C.33 CLU.P.K_SWEEP |
| 25ca1da | C.34 DR Shepard + Prophet |
| e625184 | C.35 FS10 trial barrier balance |
| bd2b871 | C.36 ANO.P.SCORE_HIST |
| 2529aed | C.37 REE.P REC / cum-error / scale-location |

## CI / Deploy / Vercel

| System | Status | Notes |
|---|---|---|
| CI | green at `2529aed` (tip `aface40` under watch) | https://github.com/ShibayanBiswas/arw-ml-lab/actions/runs/43839812689 |
| Deploy migrate | **fails** until secrets | missing `SUPABASE_ACCESS_TOKEN` / `SUPABASE_DB_PASSWORD` (`SUPABASE_PROJECT_ID` set) |
| Deploy render/smoke | skipped honestly | until `RENDER_ENABLED=true` + migrate secrets |
| Vercel | READY / **200** | https://arw-ml-lab.vercel.app |

## Blocked — needs Shibayan

1. `gh secret set SUPABASE_ACCESS_TOKEN --env production --repo ShibayanBiswas/arw-ml-lab`
2. `gh secret set SUPABASE_DB_PASSWORD --env production --repo ShibayanBiswas/arw-ml-lab`
3. Pay/approve Render Blueprint → `vars.RENDER_ENABLED=true`, `vars.LAB_API_URL`, deploy-hook secrets, Vercel `NEXT_PUBLIC_LAB_API_URL`
4. `NVIDIA_API_KEY` in Render `lab-shared` only
5. Vendor `vendor/tradinglab` for FS11–18 + AFML parity
6. Optional: GitHub Pro branch protection; Supabase Storage 2 GB

## STRESS_TEST

Closed/partial: deploy honesty, PV deepen, DL leakage scaler, import allowlist, maintenance reaper, KS drift, LIME/DiCE/ALE/EBM, **ONNX parity**, FS6–10/14–15/19–20, WFO retune, GARCH, F* expand, DR/CLU/ANO catalogue plots, REE.P deepen, e2e httpx + Locust + optional Playwright/axe, ModulePlaceholder routing. Still open: TradingLab FS11–13/16–18, Anchors (BSL), full CLE.P/REE.P/F*/TS.P.*, default CI Playwright browsers, Render hosted smoke.

## Next

Continue agent work on remaining catalogues and §39.13 AC — then replace this interim FINAL_REPORT when the hosted stack is unblocked.
