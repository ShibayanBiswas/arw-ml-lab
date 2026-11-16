# Phase oneshot-c63 — F18 AutoMFLES

## Built
- `forecast_auto_mfles` — statsforecast `AutoMFLES` with `n_windows=2` for CI speed.
- Catalogue id `auto_mfles`.

## Tests
```
uv run pytest tests/unit/test_ts_auto_mfles.py -q --tb=short
.                                                                        [100%]
```
