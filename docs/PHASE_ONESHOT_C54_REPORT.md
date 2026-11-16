# Phase oneshot-c54 — F22 VARMAX

## Built
- `forecast_varmax` — statsmodels `VARMAX(order=(1,0))` with `maxiter=50` for CI speed.
- Catalogue + `forecast("varmax", Y, h)`.

## Tests
```
uv run pytest tests/unit/test_ts_varmax.py -q --tb=short
.                                                                        [100%]
```
