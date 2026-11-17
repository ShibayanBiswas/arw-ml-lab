# Phase oneshot-c111 — DR.P.CORR_CIRCLE

## Built
- `pca_correlation_circle` in `labcore/unsupervised/dr_plots.py` — standardised PCA variable × PC correlations on the unit circle (PC_x × PC_y); |r| > 0.4 highlighted; artefact id **`DR.P.CORR_CIRCLE`**; `random_state=42`.
- API `POST /api/v1/unsupervised/dr/correlation-circle` (`pc_x`, `pc_y` on `UnsupBody`).

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests/unit/test_dr_corr_circle.py tests/unit/test_import_allowlist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 4 items

tests\unit\test_dr_corr_circle.py ...                                    [ 75%]
tests\unit\test_import_allowlist.py .                                    [100%]

============================= 4 passed in 16.16s ==============================
```

## Notes
- Seed 42 via sklearn PCA `random_state`; correlations verified with `numpy.corrcoef` vs standardised columns and PC scores.
- Distinct from c109 **`DR.P.LOADINGS`**, c107 **`DR.P.BIPLOT`**, c110 ST-OPS-07 storage purge.
- Next gap: `FS.P.VOL`, remaining CLU·DR·ANO plots per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Thin wrapper; sklearn PCA + numpy corrcoef only (rule 70).
- [x] Import allowlist green.