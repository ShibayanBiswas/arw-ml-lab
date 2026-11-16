# Phase oneshot-c13 report — ALE + TS catalogue expand

**Date:** 16 Nov 2026

## Built
- `labcore/explain/ale.py` — PyALE 1D ALE (`EXPLAIN.T.ALE`); API method `ale`.
- TS models: `auto_arima`, `naive`, `seasonal_window_average` (statsforecast).
- ExplainWorkbench + API include ALE.

## Tests (real)
```
pytest tests/unit/test_explain_ale_ts_expand.py -q
# .... passed (ALE centred; catalogue; naive/SWA; AutoARIMA)
```

## TODOs
- Full F* / TS.P.* plot matrix still open.
- Prophet / arch GARCH deferred to later slice.
