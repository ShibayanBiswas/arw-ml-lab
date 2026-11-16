# ARW ML Lab — One-shot finish report (interim)

**Date:** 16 Nov 2026 (IST)  
**Tip:** `d9c8ab3` (c42 CrostonOptimized/IMAPA/SES; CI green)  
**Live frontend:** https://arw-ml-lab.vercel.app/login → **200**  
**Repo:** https://github.com/ShibayanBiswas/arw-ml-lab

Honest interim closeout. Chunk A + deep B/C slices shipped with repeated **CI green**. Full AC closure for 4A→8.2 and every STRESS_TEST item is **not** done. Hosted Deploy remains blocked on secrets/Render payment.

## Per-phase status

| Phase | Status | Evidence |
|---|---|---|
| 0–2B, 8.1 thin | done | `docs/PHASE_*_REPORT.md` |
| 2 deepen | partial | registry (~84), Halving/NSGA-II/Hyperband, CLE.P + slices |
| 2A deepen | partial | train-window-only scaler; DeepWorkbench |
| 3 deepen | partial | LIME/DiCE/ALE/EBM + **ONNX/skops**; Anchors off (BSL) |
| 3A deepen | partial | PV02/03/10/14/15, Celery batch ≤1M, cancel |
| 4 / 4A | partial | F1–F15/F20/F24/F25 expanding (statsforecast + arch + Prophet) |
| 5B | partial | **FS1–FS15**, FS19–20; FS16–18 deferred (TradingLab) |
| 5 / 5A | partial | purged/CPCV + PBO; WFO Ridge retune |
| 6 / 6A / 6B | partial | unsupervised + VLM guards + CLU/DR/ANO/CLE/REE plots |
| 7 / 8.2 | partial | reports/e2e/Locust/ZAP/Playwright opt-in; maintenance reaper |

## Recent one-shot (c28–c42)

preprocess API → ONNX/skops → F*/FS7–13 → CLE/REE/CLU/DR/ANO plots → fairlearn slices → CrostonOptimized/IMAPA/SES

## CI / Deploy / Vercel

| System | Status | Notes |
|---|---|---|
| CI | green at `d9c8ab3` | https://github.com/ShibayanBiswas/arw-ml-lab/actions/runs/43849220081 |
| Deploy migrate | **fails** until secrets | `SUPABASE_ACCESS_TOKEN` / `SUPABASE_DB_PASSWORD` missing (`PROJECT_ID` set) |
| Deploy render/smoke | skipped honestly | until `RENDER_ENABLED=true` |
| Vercel | READY / **200** | https://arw-ml-lab.vercel.app |

## Blocked — needs Shibayan

1. `gh secret set SUPABASE_ACCESS_TOKEN --env production --repo ShibayanBiswas/arw-ml-lab`
2. `gh secret set SUPABASE_DB_PASSWORD --env production --repo ShibayanBiswas/arw-ml-lab`
3. Pay/approve Render Blueprint → `vars.RENDER_ENABLED=true`, `vars.LAB_API_URL`, deploy hooks, Vercel `NEXT_PUBLIC_LAB_API_URL`
4. `NVIDIA_API_KEY` in Render `lab-shared` only
5. Vendor `vendor/tradinglab` for FS16–18 + AFML parity
6. Optional: GitHub Pro branch protection; Supabase Storage 2 GB

## STRESS_TEST

Closed/partial: deploy honesty, ONNX, FS1–15, explain suite, WFO/GARCH, unsupervised/eval catalogues, e2e httpx + Locust + optional Playwright. Open: FS16–18/TradingLab, Anchors (BSL), full CLE.P/REE.P/F* matrices, Playwright browsers in CI, Render smoke.

## Next

Continue agent work on remaining F*/§36/§39; replace interim FINAL when hosted stack is unblocked.
