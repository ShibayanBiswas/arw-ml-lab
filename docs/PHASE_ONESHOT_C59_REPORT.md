# Phase oneshot-c59 — F11 SARIMAX

## Built
- `forecast_sarimax` — statsmodels SARIMAX(0,1,1)(0,1,1)m with future-known exog (default: linear time index).
- Catalogue id `sarimax`.

## Tests
```
uv run pytest tests/unit/test_ts_sarimax.py -q --tb=short
.                                                                        [100%]
```
