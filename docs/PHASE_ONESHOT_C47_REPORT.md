# Phase oneshot-c47 — F16 TBATS + F18 MFLES

## Built
- `forecast_mfles` — statsforecast `MFLES` (max_rounds=25, changepoints=False for CI).
- `forecast_tbats` — statsforecast `TBATS` constrained (`use_boxcox=False`, no ARMA errors).
- Catalogue + `forecast()` dispatcher keys `mfles`, `tbats`.
- HorizonGuard seasonal gate on TBATS; MFLES falls back to non-seasonal when gated.

## Tests
```
uv run pytest tests/unit/test_ts_mfles_tbats.py tests/unit/test_ts_ucm.py -q --tb=short
....                                                                     [100%]
```

## Notes
- AutoTBATS / AutoMFLES left for a later deepen (selection is slow in CI).
