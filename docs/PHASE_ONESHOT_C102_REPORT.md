# Phase oneshot-c102 — DR.P.SCREE

## Built
- `pca_scree` in `labcore/unsupervised/dr_plots.py` — standardised PCA eigenvalues (sklearn `explained_variance_`), Kaiser count (λ > 1), cumulative-variance k at 80/90/95%; artefact id **`DR.P.SCREE`**; `random_state=42`.
- API `POST /api/v1/unsupervised/dr/scree`.

## Tests
```
uv run pytest tests/unit/test_import_allowlist.py tests/unit/test_dr_scree.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 2 items

tests\unit\test_import_allowlist.py .                                    [ 50%]
tests\unit\test_dr_scree.py .                                            [100%]

============================= 2 passed in 15.57s ==============================
```

## Notes
- Seed 42 via sklearn PCA `random_state`.
- Distinct from oneshot-c101 **`FS.P.GRID`** (suitability), c100 **`F60 pmdarima_auto_arima`**, and c34 **`DR.P.SHEPARD`**.
- Next gap: `DR.P.CUMVAR` / biplot, `CLU.P.SILHOUETTE`, `ANO.P.RANKED`, remaining FS.P.* / CLU·DR·ANO plots per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Thin wrapper; sklearn PCA only (rule 70).
- [x] Import allowlist green.