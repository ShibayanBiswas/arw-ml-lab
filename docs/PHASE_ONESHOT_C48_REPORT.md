# Phase oneshot-c48 — CLE.P.COST_CURVE + CLE.P.CLASS_BALANCE

## Built
- `plot_cost_curve` — expected cost vs threshold from sklearn `roc_curve` (thin FP/FN × costs).
- `plot_class_balance` — grouped bars before/after resampling counts.

## Tests
```
uv run pytest tests/unit/test_cle_cost_balance.py -q --tb=short
.                                                                        [100%]
```
