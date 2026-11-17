# Phase oneshot-c116 — FS.P.PRICE

## Built
- `compute_cusum_filter_events` in `labcore/suitability/fs_checks.py` — shared symmetric CUSUM filter (AFML ch. 2); `check_fs9_event_count` delegates to it.
- `plot_price_cusum` in `labcore/suitability/plots.py` — close line with upward/downward CUSUM markers; artefact id **`FS.P.PRICE`**.
- API `POST /api/v1/suitability/plots/price` (sample `DS30` or rows; optional `vol_span`, `cusum_mult`, `price_col`).

## Tests
```
.\.venv\Scripts\python.exe -m ruff check labcore/suitability/plots.py labcore/suitability/fs_checks.py labcore/suitability/__init__.py backend/app/routers/suitability.py tests/unit/test_fs_price.py
# All checks passed!

.\.venv\Scripts\python.exe -m pytest tests/unit/test_fs_price.py tests/unit/test_fs_barriers.py tests/unit/test_fs_vol.py tests/unit/test_import_allowlist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 7 items

tests\unit\test_fs_price.py ..                                           [ 28%]
tests\unit\test_fs_barriers.py ..                                        [ 57%]
tests\unit\test_fs_vol.py ..                                             [ 85%]
tests\unit\test_import_allowlist.py .                                    [100%]

============================= 7 passed in 10.02s ==============================
```

## Notes
- Seed **42** on artefact metadata; default `h = 1.0×σ̄` (EWMA span 100) matches FS9 on NIFTY oracle.
- Distinct from c114 **`FS.P.BARRIERS`**, c112 **`FS.P.VOL`**, c115 **`CLU.P.CH`**.
- Next gap: `FS.P.UNIQUENESS`, `FS.P.HOLDING`, `CLU.P` (DB/gap vs k, dendrogram), remaining DR·ANO plots per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Thin wrapper; pandas EWMA + symmetric CUSUM + Plotly only (rule 70).
- [x] Import allowlist green; FS9 / vol / barriers regressions green.