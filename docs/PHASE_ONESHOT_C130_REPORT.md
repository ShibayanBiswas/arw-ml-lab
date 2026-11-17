# Phase oneshot-c130 — FS.P.SADF

## Built
- `labcore/finance/sadf.py` — `compute_sadf_series`: backward-window supremum ADF via `statsmodels.tsa.stattools.adfuller` (Phillips–Shi–Yu 2015; `max_lookback` + `end_step` for long series).
- `plot_sadf` in `labcore/suitability/plots.py` — dual-axis SADF + log price; artefact id **`FS.P.SADF`**; peak marker.
- API `POST /api/v1/suitability/plots/sadf` — `min_window`, `max_lookback`, `sadf_maxlag`, `sadf_end_step` on body; seed **42** in numbers.

## Tests
```
.\.venv\Scripts\python.exe -m ruff check labcore/finance/sadf.py labcore/suitability/plots.py labcore/suitability/__init__.py backend/app/routers/suitability.py tests/unit/test_fs_sadf.py
# All checks passed!

.\.venv\Scripts\python.exe -m pytest tests/unit/test_fs_sadf.py tests/unit/test_fs_min_ffd.py tests/unit/test_import_allowlist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 5 items

tests\unit\test_fs_sadf.py ..                                            [ 40%]
tests\unit\test_fs_min_ffd.py ..                                         [ 80%]
tests\unit\test_import_allowlist.py .                                    [100%]

============================= 5 passed in 18.56s ==============================
```

## Notes
- Seed **42** on artefact metadata; NIFTY daily (`n_obs=1235`, `end_step=3`): **peak SADF≈1.864** at **index 1230** (live run).
- Distinct from c127 **`FS.P.MIN_FFD`** (d vs ADF scan) and c129 **`FE.WB.UNSUP_ANOM`** lane.
- FS16–FS18 suitability checks stay DEFERRED until TradingLab adapters; plot is informational only.
- No Contabo changes.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest + live peak pasted from runs.
- [x] statsmodels ADF supremum wrapper (rule 70; TradingLab `get_sadf` still absent).
- [x] Import allowlist green; MIN_FFD regression green.