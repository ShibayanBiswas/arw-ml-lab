# Phase oneshot-c115 — CLU.P.CH

## Built
- `kmeans_calinski_harabasz` in `labcore/unsupervised/cluster_plots.py` — standardised KMeans per k, `sklearn.metrics.calinski_harabasz_score` (higher is better); best-k marker + vline; artefact id **`CLU.P.CH`**; `random_state=42`.
- API `POST /api/v1/unsupervised/clustering/ch`.

## Tests
```
.\.venv\Scripts\python.exe -m ruff check labcore/unsupervised/cluster_plots.py backend/app/routers/unsupervised.py tests/unit/test_cluster_ch.py
# All checks passed!

.\.venv\Scripts\python.exe -m pytest tests/unit/test_cluster_ch.py tests/unit/test_cluster_elbow.py tests/unit/test_cluster_k_sweep.py tests/unit/test_cluster_silhouette.py tests/unit/test_import_allowlist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 5 items

tests\unit\test_cluster_ch.py .                                          [ 20%]
tests\unit\test_cluster_elbow.py .                                       [ 40%]
tests\unit\test_cluster_k_sweep.py .                                     [ 60%]
tests\unit\test_cluster_silhouette.py .                                  [ 80%]
tests\unit\test_import_allowlist.py .                                    [100%]

============================= 5 passed in 37.68s ==============================
```

## Notes
- Seed **42** on KMeans and artefact metadata; iris sanity run: `best_k_by_ch=2`, best CH ≈ 251.35.
- Distinct from c113 **`CLU.P.ELBOW`** (inertia/Kneedle), c103 **`CLU.P.SILHOUETTE`**, **`CLU.P.K_SWEEP`** (dual inertia+silhouette), and planned finance **`FS.P.PRICE`** / **`FS.P.BARRIERS`**.
- Next gap: `FS.P.PRICE`, `FS.P.BARRIERS`, `CLU.P` (DB/gap, dendrogram), remaining DR·ANO plots per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Thin wrapper; sklearn KMeans + `calinski_harabasz_score` only (rule 70).
- [x] Import allowlist green; cluster plot regressions green.