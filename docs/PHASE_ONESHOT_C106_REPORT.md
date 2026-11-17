# Phase oneshot-c106 — DR.P.CUMVAR

## Built
- `pca_cumulative_variance` in `labcore/unsupervised/dr_plots.py` — standardised PCA cumulative explained variance (%), 80/90/95% reference lines and minimum-k markers; artefact id **`DR.P.CUMVAR`**; `random_state=42`.
- API `POST /api/v1/unsupervised/dr/cumvar`.

## Tests
```
uv run pytest tests/unit/test_dr_cumvar.py tests/unit/test_import_allowlist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 2 items

tests\unit\test_dr_cumvar.py .                                           [ 50%]
tests\unit\test_import_allowlist.py .                                    [100%]

============================== 2 passed in 8.90s ==============================
```

## Notes
- Seed 42 via sklearn PCA `random_state`.
- Distinct from oneshot-c104 **`ANO.P.RANKED`**, c103 **`CLU.P.SILHOUETTE`**, and c102 **`DR.P.SCREE`** (eigenvalue scree, not cumulative-% curve).
- Next gap: Celery worker `heartbeat_at` writes (OPS-03), `FS.P.GRID`, DR biplot / loadings, remaining FS.P.* / CLU·DR plots per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Thin wrapper; sklearn PCA only (rule 70).
- [x] Import allowlist green.