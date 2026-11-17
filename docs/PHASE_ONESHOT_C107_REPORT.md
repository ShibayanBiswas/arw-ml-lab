# Phase oneshot-c107 — DR.P.BIPLOT

## Built
- `pca_biplot` in `labcore/unsupervised/dr_plots.py` — standardised PCA scores on PC_x × PC_y with loading arrows (loadings = components × √λ); |loading| > 0.4 highlighted; artefact id **`DR.P.BIPLOT`**; `random_state=42`.
- API `POST /api/v1/unsupervised/dr/biplot` (`pc_x`, `pc_y` on request body).

## Tests
```
uv run pytest tests/unit/test_dr_biplot.py tests/unit/test_import_allowlist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 3 items

tests\unit\test_dr_biplot.py ..                                          [ 66%]
tests\unit\test_import_allowlist.py .                                    [100%]

============================= 3 passed in 38.92s ==============================
```

## Notes
- Seed 42 via sklearn PCA `random_state`.
- Distinct from c106 **`DR.P.CUMVAR`**, c102 **`DR.P.SCREE`**, and c34 **`DR.P.SHEPARD`**.
- Next gap: loadings heatmap / correlation circle, remaining FS.P.* (e.g. VOL, BARRIERS), Celery `heartbeat_at` (OPS-03).

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Thin wrapper; sklearn PCA only (rule 70).
- [x] Import allowlist green.