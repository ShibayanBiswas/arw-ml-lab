# Phase oneshot-c49 — F9 ARIMA + CLE/REE metric folds + density

## Built
- `forecast_arima` — statsforecast `ARIMA(order=(1,1,1))` (F9).
- `CLE.P.METRIC_FOLDS` — box/strip of fold metrics.
- `REE.P.METRIC_FOLDS`, `REE.P.TARGET_PRED_DENSITY` (gaussian_kde), `REE.P.PCT_ERR_DIST`.

## Tests
```
uv run pytest tests/unit/test_ts_arima_metric_folds.py -q --tb=short
..                                                                       [100%]
```
