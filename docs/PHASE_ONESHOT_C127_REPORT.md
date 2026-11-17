# Phase oneshot-c127 — FS.P.MIN_FFD

## Built
- `labcore/finance/ffd.py` — `get_weights_ffd`, `frac_diff_ffd`, `scan_min_ffd` (AFML fixed-width FFD + statsmodels ADF grid; seed 42 on artefact only).
- `plot_min_ffd` in `labcore/suitability/plots.py` — dual-axis ADF statistic vs *d* and correlation with log price; artefact id **`FS.P.MIN_FFD`**.
- FS15 `check_fs15_stationarity` reports numeric `ffd_d_star` (no longer deferred).
- API `POST /api/v1/suitability/plots/min-ffd` — `d_step` on body (default 0.05), seed 42 in numbers.

## Tests
```
.\.venv\Scripts\python.exe -m ruff check labcore/finance/ffd.py labcore/suitability/plots.py labcore/suitability/fs_checks.py labcore/suitability/__init__.py backend/app/routers/suitability.py tests/unit/test_fs_min_ffd.py
# All checks passed!

.\.venv\Scripts\python.exe -m pytest tests/unit/test_fs_min_ffd.py tests/unit/test_fs_holding.py tests/unit/test_fs_uniqueness.py tests/unit/test_import_allowlist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 7 items

tests\unit\test_fs_min_ffd.py ..                                         [ 28%]
tests\unit\test_fs_holding.py ..                                         [ 57%]
tests\unit\test_fs_uniqueness.py ..                                      [ 85%]
tests\unit\test_import_allowlist.py .                                    [100%]

============================= 7 passed in 12.45s ==============================
```

## Notes
- Seed **42** on artefact metadata; NIFTY daily (`n_obs=1235`): **d\* = 0.5** at `d_step=0.05` (live run).
- Distinct from c126 **`ANO.P.SCORE_HIST`** (histogram), c125 **`ANO.P.EMBED`**, and c121 **`FS.P.HOLDING`**.
- Next gap: `FS.P.SADF`, `FS.P.TRENDSCAN`, remaining ANO·DR catalogue plots per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest + live d* pasted from runs.
- [x] statsmodels ADF + thin causal FFD (rule 70; TradingLab submodule still absent).
- [x] Import allowlist green; FS holding/uniqueness regression green.