# ARW ML Lab — One-shot finish report (interim)

**Date:** 16 Nov 2026 (IST)  
**Tip:** `b184167` (CI green — ONNX mypy fix; c29–c33 catalogues)  
**Live frontend:** https://arw-ml-lab.vercel.app/login → **200**  
**Repo:** https://github.com/ShibayanBiswas/arw-ml-lab

Honest interim closeout. Chunk A + deep B/C slices shipped with repeated **CI green**. Full AC closure for 4A→8.2 and every STRESS_TEST item is **not** done. Hosted Deploy remains blocked on secrets/Render payment.

## Per-phase status

| Phase | Status | Evidence |
|---|---|---|
| 0–2B, 8.1 thin | done | `docs/PHASE_*_REPORT.md` |
| 2 deepen | partial | expanded registry (~84), Halving + NSGA-II/Hyperband, CLE.P deepen (c29) |
| 2A deepen | partial | train-window-only scaler; DeepWorkbench |
| 3 deepen | partial | LIME/DiCE/ALE/EBM + **ONNX/skops export** (c29); Anchors off (BSL) |
| 3A deepen | partial | PV02/03/10/14/15, Celery batch ≤1M, cancel |
| 4 deepen | partial | AutoARIMA/Naive/SWA/GARCH + F3/F6/F7/F14/F15/F25 (c30) |
| 4A | partial | metrics/models expand — not full F*/TS.P.* |
| 5B | partial | FS1–FS9, FS14–15, FS19–20; FS10–13/16–18 deferred |
| 5 | partial | purged/CPCV + PBO in-lab |
| 5A | partial | WFO planner + Ridge OOS retune loop |
| 6 | partial | unsupervised API/UI + mock AI insights |
| 6A | partial | deterministic VLM guards |
| 6B | not started | |
| 7 | partial | reports/drift/UI + httpx e2e + Locust + ZAP + Playwright/axe opt-in |
| 8.2 | partial | maintenance reaper/retention |

## Recent one-shot commits

| Commit | Summary |
|---|---|
| 22147fa | C.27 sklearn pipeline graph HTML |
| 95c0e62 | C.28 preprocess `/pipeline-graph` API |
| 6ad7cd7 | C.29 CLE.P deepen + ONNX/skops |
| 3c4b02e | C.30 F* expand + FS7/FS9 |
| 9796284 / 4ddcf5f | mypy overrides for onnx/skops |

See earlier rows in git log for C.1–C.26.

## CI / Deploy / Vercel

| System | Status | Notes |
|---|---|---|
| CI | green at `b184167` | https://github.com/ShibayanBiswas/arw-ml-lab/actions/runs/43836655024 |
| Deploy migrate | **fails** until secrets | missing `SUPABASE_ACCESS_TOKEN` / `SUPABASE_DB_PASSWORD` (`SUPABASE_PROJECT_ID` is set) |
| Deploy render/smoke | skipped honestly | until `RENDER_ENABLED=true` + migrate secrets |
| Vercel | READY / **200** | https://arw-ml-lab.vercel.app |

## Blocked — needs Shibayan

1. `gh secret set SUPABASE_ACCESS_TOKEN --env production --repo ShibayanBiswas/arw-ml-lab`
2. `gh secret set SUPABASE_DB_PASSWORD --env production --repo ShibayanBiswas/arw-ml-lab`
3. Pay/approve Render Blueprint → `vars.RENDER_ENABLED=true`, `vars.LAB_API_URL`, deploy-hook secrets, Vercel `NEXT_PUBLIC_LAB_API_URL`
4. `NVIDIA_API_KEY` in Render `lab-shared` only
5. Vendor `vendor/tradinglab` for FS10–18 + AFML parity
6. Optional: GitHub Pro branch protection; Supabase Storage 2 GB

## STRESS_TEST

Closed/partial this one-shot: deploy honesty, PV deepen, DL leakage scaler, import allowlist, maintenance reaper, KS drift, LIME/DiCE/ALE/EBM, **ONNX parity**, FS6–9/14–15/19–20, WFO retune, GARCH, F* expand, e2e httpx + Locust + optional Playwright/axe, ModulePlaceholder routing. Still open: TradingLab FS10–13/16–18, Anchors (BSL), full CLE.P/REE.P/F*/TS.P.*, default CI Playwright browsers, Render hosted smoke.

## Next

Continue agent work on remaining catalogues, Playwright default path, §39.13 AC — then replace this interim FINAL_REPORT when tip CI is green.
