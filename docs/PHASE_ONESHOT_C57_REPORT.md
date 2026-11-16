# Phase oneshot-c57 — UCM local linear trend (F19/F26)

## Built
- `forecast_ucm_local_linear_trend` — statsmodels `UnobservedComponents(level="local linear trend")`.
- Catalogue id `ucm_local_linear_trend`.

## Tests
```
uv run pytest tests/unit/test_ts_ucm_trend.py -q --tb=short
.                                                                        [100%]
```
