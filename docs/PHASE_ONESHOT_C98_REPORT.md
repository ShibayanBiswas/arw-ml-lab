# Phase oneshot-c98 — F10 SARIMA

## Built
- `forecast_sarima` in `labcore/timeseries/models.py` — F10 configurable `(p,d,q)(P,D,Q)m` via statsmodels `SARIMAX`; `sarima_allowed` + `seasonal_allowed` gates; catalogue id **`sarima`**; `sarima_airline` preset delegates to the same primitive.

## Tests
```
uv run pytest tests/unit/test_import_allowlist.py tests/unit/test_ts_sarima_f10.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 5 items

tests\unit\test_import_allowlist.py .                                    [ 20%]
tests\unit\test_ts_sarima_f10.py ....                                    [100%]

============================= 5 passed in 10.24s ==============================
```

## Notes
- Seed 42 not used directly (deterministic MLE on airline hold-out); default orders match existing airline preset oracle.
- Distinct from oneshot-c96 **`REE.P.WIDTH_FITTED`** / in-flight **`REE.P.PIT`** lane and c93 **`F16 AutoTBATS`**.
- Next gap: `F60 pmdarima_auto_arima`, `FS.P.LABEL_BALANCE`, or remaining TS/CLU plots per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Thin wrapper; statsmodels only (rule 70).
- [x] Import allowlist green.