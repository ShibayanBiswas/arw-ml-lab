# Phase oneshot-c69 — REE.P.CD

## Built
- `plot_regression_cd` — Friedman + Nemenyi critical-difference diagram for regression model comparison on fold scores; uses `friedman_nemenyi` / `plot_cd_ranks` (`scipy.stats.friedmanchisquare`, `scikit_posthocs.posthoc_nemenyi_friedman`); default `higher_is_better=False` for RMSE/MAE-style metrics (negates scores before ranking).

## Tests
```
uv run pytest tests/unit/test_ree_cd.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 1 item

tests\unit\test_ree_cd.py .                                              [100%]

============================= 1 passed in 13.71s ==============================
```

## Notes
- Seed 42 `numpy.random.default_rng` for synthetic per-fold RMSE fixtures (ridge best).
- Compare-group slice after c60 `REE.P.COMPARE_BARS`; next gap: `REE.P.PVALUE_HEATMAP`.