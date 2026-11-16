# Phase oneshot-c50 — CLE.P.CM_COST / CM_DELTA / COMPARE_BARS

## Built
- `plot_cm_cost` — C_ij · N_ij heatmap (sklearn `confusion_matrix`).
- `plot_cm_delta` — model A − B confusion delta (diverging RdBu).
- `plot_compare_bars` — model scores with optional asymmetric 95% CI whiskers.

## Tests
```
uv run pytest tests/unit/test_cle_cm_compare.py -q --tb=short
.                                                                        [100%]
```
