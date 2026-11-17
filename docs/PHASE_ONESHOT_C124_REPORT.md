# Phase oneshot-c124 — CLU.P.K_DISTANCE

## Built
- `dbscan_k_distance` in `labcore/unsupervised/cluster_plots.py` — standardised features, `sklearn.neighbors.NearestNeighbors` k-th NN distances sorted descending, `kneed.KneeLocator` (convex, decreasing) → suggested `eps`; artefact id **`CLU.P.K_DISTANCE`**; `seed=42` metadata.
- API `POST /api/v1/unsupervised/clustering/k-distance` — optional `min_samples` (0 → auto `max(5, 2·dim)`).

## Tests
```
.\.venv\Scripts\python.exe -m ruff check labcore/unsupervised/cluster_plots.py backend/app/routers/unsupervised.py tests/unit/test_cluster_k_distance.py
# All checks passed!

.\.venv\Scripts\python.exe -m pytest tests/unit/test_cluster_k_distance.py tests/unit/test_cluster_reachability.py tests/unit/test_import_allowlist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 3 items

tests\unit\test_cluster_k_distance.py .                                  [ 33%]
tests\unit\test_cluster_reachability.py .                                [ 66%]
tests\unit\test_import_allowlist.py .                                    [100%]

============================= 3 passed in 29.23s ==============================
```

## Notes
- Seed **42** on artefact metadata; Iris (`min_samples=5`): **suggested eps≈0.722**, **knee index=19** (live run).
- Distinct from c123 **`CLU.P.REACHABILITY`** (OPTICS ordering), c113 **`CLU.P.ELBOW`** (KMeans WCSS knee).
- Next gap: `FS.P.MIN_FFD` / SADF / TRENDSCAN, remaining ANO·DR plots per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Thin wrapper over sklearn NearestNeighbors + kneed + Plotly (rule 70).
- [x] Import allowlist green; reachability regression green.