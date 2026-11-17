# Phase oneshot-c105 — FS.P.GRID

## Built
- `compute_trial_tb_cell`, `compute_suitability_parameter_grid` in `labcore/suitability/fs_checks.py` — §37.6 grid (4 pt/sl × 3 vertical × 3 CUSUM h = 36 trial cells); default cell = max `n_eff` among minority ≥ 15%; `compute_trial_tb_label_balance` delegates to symmetric all-bar trial (FS10 unchanged).
- `plot_suitability_grid` in `labcore/suitability/plots.py` — six Plotly heatmaps (minority share + `n_eff` per CUSUM tier); artefact id **`FS.P.GRID`**.

## Tests
```
uv run pytest tests/unit/test_fs_grid.py tests/unit/test_fs_label_balance.py tests/unit/test_import_allowlist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 6 items

tests\unit\test_fs_grid.py ...                                           [ 50%]
tests\unit\test_fs_label_balance.py ..                                   [ 83%]
tests\unit\test_import_allowlist.py .                                    [100%]

============================= 6 passed in 16.97s ==============================
```

## Notes
- Seed 42 on grid metadata; oracle NIFTY `nifty50_daily_5y.csv`.
- Distinct from c106 **`DR.P.CUMVAR`** (9ae8174), c104 **`ANO.P.RANKED`**, c99 **`FS.P.LABEL_BALANCE`**.
- Next gap: Celery worker `heartbeat_at` writes (OPS-03 task path), DR biplot, remaining FS.P.* / CLU·DR·ANO plots per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Thin AFML-equivalent trial labels only (pandas/numpy); Plotly on computed grid (rule 70).
- [x] Import allowlist green; FS10 label-balance regression green.