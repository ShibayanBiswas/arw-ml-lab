# Phase oneshot-c66 — CLE.P.CONFORMAL

## Built
- `plot_conformal` — prediction-set size histogram plus empirical coverage by true class; overall coverage and mean set size via `mapie.metrics.classification` (`classification_coverage_score`, `classification_mean_width_score`); accepts MAPIE APS set tensors `(n, k)` or `(n, k, 1)`.

## Tests
```
uv run pytest tests/unit/test_cle_conformal.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 2 items

tests\unit\test_cle_conformal.py ..                                      [100%]

============================== 2 passed in 9.49s ==============================
```