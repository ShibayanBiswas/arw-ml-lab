# Phase oneshot-c117 — CLU.P.DB

## Built
- `kmeans_davies_bouldin` in `labcore/unsupervised/cluster_plots.py` — standardised KMeans per k, `sklearn.metrics.davies_bouldin_score` (lower is better); min-DB marker + vline; artefact id **`CLU.P.DB`**; `random_state=42`.
- API `POST /api/v1/unsupervised/clustering/db`.

## Tests
```
.\.venv\Scripts\python.exe -m ruff check labcore/unsupervised/cluster_plots.py backend/app/routers/unsupervised.py tests/unit/test_cluster_db.py
# All checks passed!

.\.venv\Scripts\python.exe -m pytest tests/unit/test_cluster_db.py tests/unit/test_cluster_ch.py tests/unit/test_cluster_elbow.py tests/unit/test_cluster_k_sweep.py tests/unit/test_cluster_silhouette.py tests/unit/test_import_allowlist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 6 items

tests\unit\test_cluster_db.py .                                          [ 16%]
tests\unit\test_cluster_ch.py .                                          [ 33%]
tests\unit\test_cluster_elbow.py .                                       [ 50%]
tests\unit\test_cluster_k_sweep.py .                                     [ 66%]
tests\unit\test_cluster_silhouette.py .                                  [ 83%]
tests\unit\test_import_allowlist.py .                                    [100%]

============================= 6 passed in 42.60s ==============================
```

## Notes
- Seed **42** on KMeans and artefact metadata; iris sanity run: `best_k_by_db=2`, best DB ≈ 0.593.
- Mirrors c115 **`CLU.P.CH`** (same k-sweep layout; CH maximises, DB minimises).
- Next gap: `CLU.P` gap vs k, dendrogram + cophenetic, `FS.P.PRICE`, remaining DR·ANO plots per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Thin wrapper; sklearn KMeans + `davies_bouldin_score` only (rule 70).
- [x] Import allowlist green; cluster plot regressions green.