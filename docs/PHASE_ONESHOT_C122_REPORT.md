# Phase oneshot-c122 — CLU.P.CLUSTERMAP

## Built
- `correlation_clustermap` in `labcore/unsupervised/cluster_plots.py` — standardised feature Pearson *r* matrix, √(2(1−*r*)) linkage (`scipy.cluster.hierarchy` + `squareform`), leaf reordering, Plotly heatmap with top/left dendrogram segments; artefact id **`CLU.P.CLUSTERMAP`**; `seed=42` in metadata.
- API `POST /api/v1/unsupervised/clustering/clustermap`.

## Tests
```
.\.venv\Scripts\python.exe -m ruff check tests/unit/test_cluster_clustermap.py labcore/unsupervised/cluster_plots.py backend/app/routers/unsupervised.py
# (optics_reachability E741 in cluster_plots pre-exists this commit)

.\.venv\Scripts\python.exe -m pytest tests/unit/test_cluster_clustermap.py tests/unit/test_cluster_dendrogram.py tests/unit/test_import_allowlist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 3 items

tests\unit\test_cluster_clustermap.py .                                  [ 33%]
tests\unit\test_cluster_dendrogram.py .                                  [ 66%]
tests\unit\test_import_allowlist.py .                                    [100%]

============================= 3 passed in 18.82s ==============================
```

## Notes
- Seed **42** on artefact metadata; Iris (4 features, average linkage): **cophenetic r=0.989**, leaf order `['f1', 'f0', 'f2', 'f3']` (live run).
- Plot/API landed in commit `c753353` together with **`CLU.P.REACHABILITY`**; this step adds the dedicated unit test and phase report for **`CLU.P.CLUSTERMAP`**.
- Distinct from c118 **`CLU.P.DENDROGRAM`** (sample hierarchical tree) and c123 **`CLU.P.REACHABILITY`** (OPTICS ordering).
- Next gap: k-distance, `FS.P.MIN_FFD` / SADF / TRENDSCAN, remaining ANO·DR plots per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Thin wrapper over scipy/sklearn/Plotly (rule 70).
- [x] Import allowlist green; dendrogram regression green.