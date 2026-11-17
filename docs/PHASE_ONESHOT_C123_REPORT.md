# Phase oneshot-c123 — CLU.P.REACHABILITY

## Built
- `optics_reachability` in `labcore/unsupervised/cluster_plots.py` — standardised features, `sklearn.cluster.OPTICS` (`cluster_method=xi`, `n_jobs=1`); reachability reordered by `ordering_`; cluster-coloured valleys + noise segment; artefact id **`CLU.P.REACHABILITY`**; `seed=42` in metadata (OPTICS is deterministic for fixed data/metric).
- API `POST /api/v1/unsupervised/clustering/reachability` — optional `min_samples` (0 → auto `max(5, 2·dim)`), `max_eps` (0 → inf), `cluster_method`, `xi`.

## Tests
```
.\.venv\Scripts\python.exe -m ruff check labcore/unsupervised/cluster_plots.py backend/app/routers/unsupervised.py tests/unit/test_cluster_reachability.py
# All checks passed!

.\.venv\Scripts\python.exe -m pytest tests/unit/test_cluster_reachability.py tests/unit/test_cluster_dendrogram.py tests/unit/test_cluster_gap.py tests/unit/test_import_allowlist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 4 items

tests\unit\test_cluster_reachability.py .                                [ 25%]
tests\unit\test_cluster_dendrogram.py .                                  [ 50%]
tests\unit\test_cluster_gap.py .                                         [ 75%]
tests\unit\test_import_allowlist.py .                                    [100%]

============================= 4 passed in 44.11s ==============================
```

## Notes
- Seed **42** on artefact metadata; Iris (`min_samples=5`): **n_clusters=5**, **n_noise=109** (from live run).
- Distinct from c121 **`FS.P.HOLDING`**, c118 **`CLU.P.DENDROGRAM`**, c119 **`CLU.P.GAP`**, and planned c122 **`CLU.P.CLUSTERMAP`** (not shipped here).
- Next gap: **`CLU.P.K_DISTANCE`** (DBSCAN eps knee), `CLU.P.CLUSTERMAP`, `FS.P.MIN_FFD` / SADF / TRENDSCAN, remaining ANO·DR plots per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Thin wrapper over sklearn OPTICS + Plotly (rule 70).
- [x] Import allowlist green; clustering plot regressions green.