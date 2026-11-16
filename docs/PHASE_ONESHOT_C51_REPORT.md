# Phase oneshot-c51 — F13 ARIMA + Fourier

## Built
- `forecast_arima_fourier` — `utilsforecast.feature_engineering.fourier` exogenous + statsforecast `ARIMA(1,1,1)`.
- HorizonGuard seasonal gate; catalogue id `arima_fourier`.

## Tests
```
uv run pytest tests/unit/test_ts_arima_fourier.py -q --tb=short
.                                                                        [100%]
```
