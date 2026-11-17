# Phase oneshot-c100 — F60 pmdarima AutoARIMA

## Built
- `forecast_pmdarima_auto_arima` in `labcore/timeseries/models.py` — F60 stepwise `pmdarima.auto_arima` with KPSS + OCSB seasonal test, AICc, AR/MA caps per ARCHITECTURE; HorizonGuard seasonal toggle matches statsforecast `auto_arima`; catalogue id **`pmdarima_auto_arima`**; `random_state=42`.

## Tests
```
uv run pytest tests/unit/test_import_allowlist.py tests/unit/test_ts_pmdarima_f60.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 4 items

tests\unit\test_import_allowlist.py .                                    [ 25%]
tests\unit\test_ts_pmdarima_f60.py ...                                   [100%]

============================= 4 passed in 22.53s ==============================
```

## Notes
- Seed 42 via pmdarima `random_state`.
- `pytest.importorskip("pmdarima")` — same pattern as F20 Prophet (train image / `ts.txt` only).
- Distinct from oneshot-c99 **`FS.P.LABEL_BALANCE`**, c98 **`F10 SARIMA`**, and c97 **`REE.P.PIT`**.
- Next gap: `FS.P.GRID`, remaining FS.P.* / CLU·DR·ANO plots per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Thin wrapper; pmdarima only (rule 70).
- [x] Import allowlist green.