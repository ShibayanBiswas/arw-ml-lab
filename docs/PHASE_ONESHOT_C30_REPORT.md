# Phase oneshot-c30 — F* expand + FS7/FS9

## Built
- TS catalogue: F3 RandomWalkWithDrift, F6 Holt, F7 HoltWinters, F14 AutoTheta, F15 AutoCES, F4 WindowAverage, F25 CrostonClassic (+ shared `_sf_point_forecast`).
- FS7 EWMA daily vol (pandas `ewm(span=100).std` on returns) — AFML `get_daily_vol` equivalent until TradingLab submodule.
- FS9 CUSUM event count with h = mean EWMA σ — AFML `cusum_filter` thin.

## Tests
```
pytest tests/unit/test_ts_f_expand_c30.py \
  tests/unit/test_unsupervised_suitability.py::test_fs6_fs8_fs15_fs19_nifty -q
→ 3 passed
```

## Still deferred
- FS10–FS13, FS16–FS18 (TradingLab labels / uniqueness / meta)
- Anchors (BSL), Render hosted smoke, Playwright/axe
