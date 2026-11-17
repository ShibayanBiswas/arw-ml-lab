# Phase oneshot-c112 — FS.P.VOL

## Built
- `compute_daily_ewma_vol` in `labcore/suitability/fs_checks.py` — shared close-to-close EWMA σ (AFML `get_daily_vol` equivalent); `check_fs7_daily_vol` delegates to it.
- `plot_daily_volatility` in `labcore/suitability/plots.py` — Plotly time series of EWMA daily vol with median σ reference; artefact id **`FS.P.VOL`**; `seed=42` on artefact metadata.
- API `POST /api/v1/suitability/plots/volatility` (sample `DS30` or rows; optional `vol_span`, `price_col`).

## Tests
```
.\.venv\Scripts\python.exe -m ruff check labcore/suitability/plots.py labcore/suitability/fs_checks.py labcore/suitability/__init__.py backend/app/routers/suitability.py tests/unit/test_fs_vol.py
# All checks passed!

.\.venv\Scripts\python.exe -m pytest tests/unit/test_fs_vol.py tests/unit/test_fs_label_balance.py tests/unit/test_fs_grid.py tests/unit/test_import_allowlist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 8 items

tests\unit\test_fs_vol.py ..                                             [ 25%]
tests\unit\test_fs_label_balance.py ..                                   [ 50%]
tests\unit\test_fs_grid.py ...                                           [ 87%]
tests\unit\test_import_allowlist.py .                                    [100%]

============================= 8 passed in 20.82s ==============================
```

## Notes
- Seed **42** on plot metadata; oracle NIFTY `nifty50_daily_5y.csv`; `median_vol` matches FS7 check.
- Distinct from in-progress c111 **`DR.P.CORR_CIRCLE`** (uncommitted), c110 ST-OPS-07, c105 **`FS.P.GRID`**, c99 **`FS.P.LABEL_BALANCE`**.
- Next gap: `FS.P.BARRIERS`, `FS.P.PRICE`, remaining CLU·DR·ANO plots per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Thin pandas EWMA + Plotly only (rule 70).
- [x] Import allowlist green; FS7 / FS10 / grid regressions green.