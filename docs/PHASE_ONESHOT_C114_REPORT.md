# Phase oneshot-c114 — FS.P.BARRIERS

## Built
- `enumerate_trial_tb_events` / `sample_trial_tb_events` in `labcore/suitability/fs_checks.py` — trial triple-barrier geometry shared with FS10/§37.6 grid; reproducible sampling (`seed=42`).
- `plot_sample_barriers` in `labcore/suitability/plots.py` — stacked panels with close path, profit-take / stop-loss / vertical barriers; artefact id **`FS.P.BARRIERS`**.
- API `POST /api/v1/suitability/plots/barriers` (sample `DS30` or rows; optional `horizon`, `pt_mult`, `sl_mult`, `n_samples`).

## Tests
```
.\.venv\Scripts\python.exe -m ruff check labcore/suitability/plots.py labcore/suitability/fs_checks.py labcore/suitability/__init__.py backend/app/routers/suitability.py tests/unit/test_fs_barriers.py
# All checks passed!

.\.venv\Scripts\python.exe -m pytest tests/unit/test_fs_barriers.py tests/unit/test_fs_vol.py tests/unit/test_fs_label_balance.py tests/unit/test_fs_grid.py tests/unit/test_import_allowlist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 10 items

tests\unit\test_fs_barriers.py ..                                        [ 20%]
tests\unit\test_fs_vol.py ..                                             [ 40%]
tests\unit\test_fs_label_balance.py ..                                   [ 60%]
tests\unit\test_fs_grid.py ...                                           [ 90%]
tests\unit\test_import_allowlist.py .                                    [100%]

============================= 10 passed in 15.38s ==============================
```

## Notes
- Seed **42** on sampling and artefact metadata; default trial params match FS10 (pt=sl=1σ, vertical=5 bars).
- Distinct from c113 **`CLU.P.ELBOW`**, c112 **`FS.P.VOL`**, c105 **`FS.P.GRID`**, c99 **`FS.P.LABEL_BALANCE`**.
- Next gap: `FS.P.PRICE`, `CLU.P.*` (CH/DB/gap vs k, dendrogram), remaining DR·ANO plots per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Thin wrapper; pandas EWMA labelling + Plotly only (rule 70).
- [x] Import allowlist green; FS7/FS10/grid regressions green.