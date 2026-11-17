# Phase oneshot-c113 — CLU.P.ELBOW

## Built
- `kmeans_elbow` in `labcore/unsupervised/cluster_plots.py` — standardised KMeans WCSS vs k with `kneed.KneeLocator` (convex, decreasing); knee marker + vline; artefact id **`CLU.P.ELBOW`**; `random_state=42`.
- API `POST /api/v1/unsupervised/clustering/elbow`.

## Tests
```
.\.venv\Scripts\python.exe -m ruff check labcore/unsupervised/cluster_plots.py backend/app/routers/unsupervised.py tests/unit/test_cluster_elbow.py
# All checks passed!

.\.venv\Scripts\python.exe -m pytest tests/unit/test_cluster_elbow.py tests/unit/test_cluster_k_sweep.py tests/unit/test_cluster_silhouette.py tests/unit/test_import_allowlist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 4 items

tests\unit\test_cluster_elbow.py .                                       [ 25%]
tests\unit\test_cluster_k_sweep.py .                                     [ 50%]
tests\unit\test_cluster_silhouette.py .                                  [ 75%]
tests\unit\test_import_allowlist.py .                                    [100%]

============================= 4 passed in 21.41s ==============================
```

## Notes
- Seed **42** on KMeans and artefact metadata; iris sanity run: `knee_k=5`, knee inertia ≈ 90.93.
- Distinct from c112 **`FS.P.VOL`**, c103 **`CLU.P.SILHOUETTE`**, and **`CLU.P.K_SWEEP`** (dual-axis scan without dedicated Kneedle knee artefact).
- Next gap: `FS.P.BARRIERS`, `FS.P.PRICE`, `CLU.P.*` (CH/DB/gap vs k, dendrogram), remaining ANO/DR plots per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Thin wrapper; sklearn KMeans + kneed only (rule 70).
- [x] Import allowlist green; cluster plot regressions green.