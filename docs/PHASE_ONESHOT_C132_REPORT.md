# Phase oneshot-c132 — FS.P.TRENDSCAN

## Built
- `labcore/finance/trendscan.py` — `compute_trendscan_series`: max-|t| forward-window slope via `scipy.stats.linregress` (AFML trend-scan; L ∈ [5, 20] default).
- `plot_trendscan` in `labcore/suitability/plots.py` — dual-axis signed t-stat + log price; ±2 reference; artefact id **`FS.P.TRENDSCAN`**; peak |t| marker.
- API `POST /api/v1/suitability/plots/trendscan` — `trendscan_l_min`, `trendscan_l_max`, `trendscan_step` on body; seed **42** in numbers.

## Tests
```
.\.venv\Scripts\python.exe -m ruff check labcore/finance/trendscan.py labcore/suitability/plots.py labcore/suitability/__init__.py backend/app/routers/suitability.py tests/unit/test_fs_trendscan.py
# All checks passed!

.\.venv\Scripts\python.exe -m pytest tests/unit/test_fs_trendscan.py tests/unit/test_fs_sadf.py tests/unit/test_import_allowlist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 5 items

tests\unit\test_fs_trendscan.py ..                                       [ 40%]
tests\unit\test_fs_sadf.py ..                                            [ 80%]
tests\unit\test_import_allowlist.py .                                    [100%]

======================== 5 passed in 60.26s (0:01:00) =========================
```

## Notes
- Seed **42** on artefact metadata; NIFTY daily (`step=3`): **peak t≈28.268** at **origin 555**; **|t|>2 share≈99.5%** (live run).
- Distinct from c130 **`FS.P.SADF`** (backward supremum ADF) and c127 **`FS.P.MIN_FFD`** (d vs ADF scan).
- FS17 suitability check stays DEFERRED until TradingLab `trend_scanning_labels`; plot is informational only.
- No Contabo changes.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest + live peak pasted from runs.
- [x] scipy linregress wrapper (rule 70; TradingLab adapter still absent).
- [x] Import allowlist green; SADF regression green.