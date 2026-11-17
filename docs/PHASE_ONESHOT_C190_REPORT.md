# Phase oneshot-c190 — FS16–FS18 thin AFML

## Built
- `labcore/suitability/fs_checks.py` — **FS16** (SADF + ruptures, INFO), **FS17** (trend-scan `|t|>2` share), **FS18** (MA-cross primary signal count); method verdicts for `trend_scanning` / `meta_labeling` no longer DEFERRED.
- `tests/unit/test_fs16_18_thin.py` — seed-42 synthetic series.
- `tests/unit/test_unsupervised_suitability.py` — NIFTY assertions updated.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_fs16_18_thin.py -v --tb=short
============================= 4 passed in 10.80s ==============================

.\.venv\Scripts\python.exe -m pytest tests\unit\test_unsupervised_suitability.py::test_fs6_fs8_fs15_fs19_nifty -v --tb=line
============================= 1 passed in 10.97s ==============================
```

## Notes
- Seed **42**. TradingLab parity adapters still deferred (`vendor/tradinglab` missing); thin labs use `labcore.finance.sadf` / `trendscan` + ruptures.
- Contabo / Actions billing still blocked.

## Self-check
- [x] FS16–18 not DEFERRED in `run_suitability`.
- [x] Interactive timing on NIFTY sample (~11s).
- [x] Rule 70: statsmodels / scipy / ruptures only.
