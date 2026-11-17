# Phase oneshot-c118 — CLU.P.DENDROGRAM

## Built
- `hierarchical_dendrogram` in `labcore/unsupervised/cluster_plots.py` — standardised Ward linkage (`scipy.cluster.hierarchy` + `pdist`); truncated last-p merges; colour threshold 0.7×max height; `hierarchy.cophenet` correlation in numbers + title; Plotly line segments (matplotlib `C*` colours mapped to tab10 hex); artefact id **`CLU.P.DENDROGRAM`**; `seed=42` in metadata.
- API `POST /api/v1/unsupervised/clustering/dendrogram` (`linkage_method`, `truncate_p`, `dendro_max_rows` on `UnsupBody`).

## Tests
```
.\.venv\Scripts\python.exe -m ruff check labcore/unsupervised/cluster_plots.py backend/app/routers/unsupervised.py tests/unit/test_cluster_dendrogram.py
# All checks passed!

.\.venv\Scripts\python.exe -m pytest tests/unit/test_cluster_dendrogram.py tests/unit/test_cluster_db.py tests/unit/test_cluster_gap.py tests/unit/test_import_allowlist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 4 items

tests\unit\test_cluster_dendrogram.py .                                  [ 25%]
tests\unit\test_cluster_db.py .                                          [ 50%]
tests\unit\test_cluster_gap.py .                                         [ 75%]
tests\unit\test_import_allowlist.py .                                    [100%]

============================= 4 passed in 29.81s ==============================
```

## Notes
- Seed **42** on artefact metadata; clustering is deterministic given data (no stochastic sampler).
- Iris sanity: cophenetic **r ≈ 0.823** (Ward, truncated p=30); oracle matches `hierarchy.cophenet` in unit test.
- Distinct from c117 **`CLU.P.DB`**, c115 **`CLU.P.CH`**, and parallel **`CLU.P.GAP`** (k-sweep / Tibshirani references).
- Next gap: clustermap, k-distance, reachability, `FS.P.UNIQUENESS` / `FS.P.HOLDING`, remaining DR·ANO plots per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Thin wrapper; scipy linkage/dendrogram/cophenet only (rule 70).
- [x] Import allowlist green; cluster plot regressions green.