# Phase oneshot-c99 — FS.P.LABEL_BALANCE

## Built
- `compute_trial_tb_label_balance` and `compute_fixed_horizon_label_balance` in `labcore/suitability/fs_checks.py` — shared trial labelling for FS10/FS19 and plots.
- `plot_label_balance` in `labcore/suitability/plots.py` — Plotly bar chart of −1 / 0 / +1 shares with 15% / 5% reference lines; artefact id **`FS.P.LABEL_BALANCE`**; methods `triple_barrier` (default) and `fixed_horizon`.

## Tests
```
uv run pytest tests/unit/test_import_allowlist.py tests/unit/test_fs_label_balance.py tests/unit/test_unsupervised_suitability.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 9 items

tests\unit\test_import_allowlist.py .                                    [ 11%]
tests\unit\test_fs_label_balance.py ..                                   [ 33%]
tests\unit\test_unsupervised_suitability.py ......                       [100%]

============================= 9 passed in 20.09s ==============================
```

## Notes
- Oracle: NIFTY sample `nifty50_daily_5y.csv`; plot `numbers` match FS10 `check_fs10_class_balance` details (no TradingLab; FS16–18 unchanged DEFERRED).
- Distinct from c98 **`F10 SARIMA`** and c97 **`REE.P.PIT`** lanes.
- Next gap: `FS.P.GRID`, F60 `pmdarima_auto_arima` (train image / `ts.txt`), or remaining FS.P.* / CLU·DR·ANO plots per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Thin AFML-equivalent trial labels only (pandas/numpy); Plotly layout on computed shares.
- [x] Import allowlist green; suitability regression tests green.