# Phase oneshot-c65 — CLE.P.MULTILABEL_BARS

## Built
- `plot_multilabel_bars` — per-label F1 bars (`sklearn.metrics.f1_score`, `average=None`) plus label-cardinality histogram on true labels; numbers include support, label density, and cardinality counts.

## Tests
```
uv run pytest tests/unit/test_cle_multilabel_bars.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 1 item

tests\unit\test_cle_multilabel_bars.py .                                 [100%]

============================== 1 passed in 7.97s ==============================
```