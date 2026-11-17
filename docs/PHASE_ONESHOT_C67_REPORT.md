# Phase oneshot-c67 — CLE.P.SLICES

## Built
- `metric_by_segment` — `fairlearn.metrics.MetricFrame` with accuracy, F1, and recall (binary vs macro by class count); grouped bar plot by segment with dotted overall reference lines per metric; `CLE.T.SLICES` table rows plus `CLE.P.SLICES` Plotly artefact with `numbers` (overall and by-segment).

## Tests
```
uv run pytest tests/unit/test_cle_slices.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 1 item

tests\unit\test_cle_slices.py .                                          [100%]

============================== 1 passed in 12.94s ==============================
```