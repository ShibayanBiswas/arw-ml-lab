# Phase oneshot-c93 — F16 AutoTBATS

## Built
- `forecast_auto_tbats` — statsforecast `AutoTBATS` with `use_arma_errors=False` for CI speed (deferred in c47 alongside fixed TBATS).
- Catalogue id `auto_tbats` (F16; complements existing `tbats`).

## Tests
```
uv run pytest tests/unit/test_import_allowlist.py tests/unit/test_ts_auto_tbats.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 3 items

tests\unit\test_import_allowlist.py .                                    [ 33%]
tests\unit\test_ts_auto_tbats.py ..                                      [100%]

============================= 3 passed in 35.43s ==============================
```

## Notes
- Seed 42 implicit via airline passengers hold-out; oracle: finite `y_pred` length `h` on DS22-style series.
- CPU only (`statsforecast`, `n_jobs=1`); no GPU worker path.
- Next gap: `F10` SARIMA (generic), `CLE.P.ROC_CV`, `REE.P.WIDTH_FITTED`, or `FS.P.LABEL_BALANCE` per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Library-only wrapper (rule 70); `AutoTBATS` from pinned statsforecast.
- [x] Import allowlist green.