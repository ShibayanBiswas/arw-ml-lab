# Phase oneshot-c120 — FS.P.UNIQUENESS

## Built
- `compute_trial_uniqueness_profile` in `labcore/suitability/fs_checks.py` — trial ±1σ spans, per-event ū_i, concurrency c_t; refactors FS12 to call it.
- `plot_uniqueness_concurrency` in `labcore/suitability/plots.py` — histogram of ū and time series of c_t; artefact id **`FS.P.UNIQUENESS`**; `seed=42` on artefact metadata.
- API `POST /api/v1/suitability/plots/uniqueness` (`horizon` / `vol_span` from `SuitabilityBody`).

## Tests
```
.\.venv\Scripts\python.exe -m ruff check labcore/suitability/fs_checks.py labcore/suitability/plots.py labcore/suitability/__init__.py backend/app/routers/suitability.py tests/unit/test_fs_uniqueness.py
# All checks passed!

.\.venv\Scripts\python.exe -m pytest tests/unit/test_fs_uniqueness.py tests/unit/test_fs_vol.py tests/unit/test_fs_price.py tests/unit/test_import_allowlist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 7 items

tests\unit\test_fs_uniqueness.py ..                                      [ 28%]
tests\unit\test_fs_vol.py ..                                             [ 57%]
tests\unit\test_fs_price.py ..                                           [ 85%]
tests\unit\test_import_allowlist.py .                                    [100%]

============================= 7 passed in 14.66s ==============================
```

## Notes
- Seed **42** on artefact metadata; NIFTY50 daily (`nifty50_daily_5y.csv`): `n_spans=1204`, mean ū ≈ 0.273, `max_concurrency=7`, `median_concurrency=4` — matches FS12 in suitability report.
- Distinct from c116 **`FS.P.PRICE`**, c119 **`CLU.P.GAP`**, planned **`FS.P.HOLDING`**.
- Next gap: `FS.P.HOLDING`, `CLU.P.DENDROGRAM`, remaining ANO·DR plots per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Thin AFML wrapper; no from-scratch estimators (rule 70).
- [x] Import allowlist green; FS plot regressions green.