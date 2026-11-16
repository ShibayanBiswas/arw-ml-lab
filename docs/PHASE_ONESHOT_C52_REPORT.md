# Phase oneshot-c52 — F21 VAR + REE.P.CALIBRATION_BINS

## Built
- `forecast_var` — statsmodels `VAR` with AIC lag selection (`maxlags=5`).
- `forecast(..., key="var")` accepts multivariate `y_train` shape `(n, k)` (optional `endog=`).
- Catalogue entry `var`.
- `plot_calibration_bins` — mean y vs mean ŷ by decile with y=x.

## Tests
```
uv run pytest tests/unit/test_ts_var.py -q --tb=short
..                                                                       [100%]
```
