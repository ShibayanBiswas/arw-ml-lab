# Phase oneshot-c121 — FS.P.HOLDING

## Built
- `compute_trial_holding_profile` in `labcore/suitability/fs_checks.py` — holding bars `t1−t0` from trial `enumerate_trial_tb_events` (±1σ default, shared with FS10).
- Restored `plot_uniqueness_concurrency` + `/plots/uniqueness` (c120 commit omitted the plot body but kept the route).
- `plot_holding_period_distribution` in `labcore/suitability/plots.py` — overlaid label-coloured histogram + mean/median vlines; artefact id **`FS.P.HOLDING`**; `seed=42` in metadata.
- API `POST /api/v1/suitability/plots/holding`.

## Tests
```
.\.venv\Scripts\python.exe -m ruff check labcore/suitability/plots.py labcore/suitability/fs_checks.py labcore/suitability/__init__.py backend/app/routers/suitability.py tests/unit/test_fs_holding.py
# All checks passed!

.\.venv\Scripts\python.exe -m pytest tests/unit/test_fs_holding.py tests/unit/test_fs_uniqueness.py tests/unit/test_fs_price.py tests/unit/test_fs_barriers.py tests/unit/test_fs_vol.py tests/unit/test_fs_label_balance.py tests/unit/test_import_allowlist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 13 items

tests\unit\test_fs_holding.py ..                                         [ 15%]
tests\unit\test_fs_uniqueness.py ..                                      [ 30%]
tests\unit\test_fs_price.py ..                                           [ 46%]
tests\unit\test_fs_barriers.py ..                                        [ 61%]
tests\unit\test_fs_vol.py ..                                             [ 76%]
tests\unit\test_fs_label_balance.py ..                                   [ 92%]
tests\unit\test_import_allowlist.py .                                    [100%]

============================= 13 passed in 9.96s ==============================
```

## Notes
- Seed **42** on artefact metadata; NIFTY trial (horizon=5, ±1σ, `cusum_mult=None`): **n_events=1204**, **mean_holding≈2.81 bars**, **median_holding=3 bars** (from live run).
- Distinct from c118 **`CLU.P.DENDROGRAM`**, c119 **`CLU.P.GAP`**, and planned **`FS.P.UNIQUENESS`** (concurrency/ū, not holding bars).
- Next gap: `FS.P.UNIQUENESS`, `FS.P.MIN_FFD` / `SADF` / `TRENDSCAN`, remaining ANO·DR plots per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Thin wrapper over existing trial TB enumerator + Plotly (rule 70).
- [x] Import allowlist green; FS plot regressions green.