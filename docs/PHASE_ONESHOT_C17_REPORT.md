# Phase oneshot-c17 — GARCH(1,1) via arch

**Date:** 16 Nov 2026

## Built
- `forecast_garch11` + catalogue entry `garch11` (Library Matrix §44 / `arch`).

## Tests
```
pytest tests/unit/test_explain_ale_ts_expand.py::test_garch11_variance_forecast -q
# . passed
```
