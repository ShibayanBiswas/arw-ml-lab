# Phase oneshot-c16 — WFO retune loop

**Date:** 16 Nov 2026

## Built
- `labcore.finance.wfo.run_wfo_regression` — per-window Ridge fit + sklearn OOS R²/MAE.
- `POST /api/v1/wfo/run` API.

## Tests
```
pytest tests/unit/test_wfo_plan.py -q
# ... passed (mean OOS R² > 0.5 on linear synthetic)
```
