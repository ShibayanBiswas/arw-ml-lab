# Phase oneshot-c109 — DR.P.LOADINGS

## Built
- `pca_loadings_heatmap` in `labcore/unsupervised/dr_plots.py` — standardised PCA loadings (components × √λ) as variable × PC heatmap; |loading| > 0.4 counted in `strong_cells`; artefact id **`DR.P.LOADINGS`**; `random_state=42`.
- API `POST /api/v1/unsupervised/dr/loadings` (`max_pcs=0` → all components).

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests/unit/test_dr_loadings.py tests/unit/test_dr_biplot.py tests/unit/test_import_allowlist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 6 items

tests\unit\test_dr_loadings.py ...                                       [ 50%]
tests\unit\test_dr_biplot.py ..                                          [ 83%]
tests\unit\test_import_allowlist.py .                                    [100%]

============================= 6 passed in 15.31s ==============================
```

## Notes
- Seed 42 via sklearn PCA `random_state`.
- Distinct from c107 **`DR.P.BIPLOT`**, c108 OPS-03 heartbeat, c102 **`DR.P.SCREE`**.
- Next gap: DR correlation circle, `FS.P.VOL`, remaining CLU·DR·ANO plots per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Thin wrapper; sklearn PCA only (rule 70).
- [x] Import allowlist green.