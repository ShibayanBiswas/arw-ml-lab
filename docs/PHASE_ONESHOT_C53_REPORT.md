# Phase oneshot-c53 — F23 VECM

## Built
- `forecast_vecm` — statsmodels `VECM` with Johansen `select_coint_rank` (trace, 5%).
- Catalogue + `forecast("vecm", Y, h)` for multivariate `(n, k)`.

## Tests
```
uv run pytest tests/unit/test_ts_vecm.py -q --tb=short
.                                                                        [100%]
```
