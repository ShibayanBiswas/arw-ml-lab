# Phase 4 report — Time Series thin

**Date:** 2026-11-15 (IST)  
**Commit message target:** `phase 4: timeseries thin`

## Built

### Engine (`labcore/timeseries/`)
- `horizon_guard.py` — §20 Steps 1–2–4 + model gates; intake re-export
- `models.py` — SeasonalNaive (statsforecast), SARIMA airline (statsmodels)
- `backtest.py` — rolling-origin expanding W windows; soft h*
- `metrics.py` — MAE, RMSE, sMAPE, MASE, Ljung-Box
- `analysis.py` — classical decompose, STL, ACF/PACF

### API / UI
- `POST /api/v1/timeseries/horizon|backtest|analysis`
- `TsWorkbench` on timeseries home/analysis/backtesting/forecast/lab

## Tests (real output)

```
.\.venv\Scripts\python.exe -m pytest tests/unit/test_horizon_guard.py tests/unit/test_phase4_timeseries.py tests/unit/test_timeseries_api.py -q
..................................                                       [100%]
# 34 passed
```

Thin ACs:
- HorizonGuard ≥20 table cases; DS22 h_max=24; DS23 ≤9
- DS22 SARIMA MASE &lt; SeasonalNaive; Ljung-Box p&gt;0.05
- DS23 seasonal gate at h=12; API 422 when h&gt;h_max

## Deviations
- Backtest AC uses h=12 (within h_max) for CI wall-time; structural h_max=24 tested separately
- Seasonal gate treats n ≤ 2m+h as disabled (strict boundary)
- Full F* / DS24 / DS28 deferred to 4-cont/4A (ADR-0014)

## Self-verification checklist (§000)
- [x] Phase 4 unit ACs green (commands above)
- [ ] CI green + Vercel `arw-ml-lab` READY only (closeout)
- [x] ADR-0014 + PROGRESS
- [x] No secrets in diff
