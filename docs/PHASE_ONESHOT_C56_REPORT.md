# Phase oneshot-c56 — REE.P.ERR_SEGMENT + ERR_HEATMAP

## Built
- `plot_err_segment` — MAE/bias by ŷ-decile via fairlearn `MetricFrame`.
- `plot_err_heatmap` — mean |e| on a 2-feature grid via `scipy.stats.binned_statistic_2d`.

## Tests
```
uv run pytest tests/unit/test_ree_err_segment.py -q --tb=short
.                                                                        [100%]
```
