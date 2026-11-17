# Phase oneshot-c119 — CLU.P.GAP

## Built
- `kmeans_gap_statistic` in `labcore/unsupervised/cluster_plots.py` — standardised KMeans log-WCSS, Tibshirani uniform reference sets (B=`n_refs`), Gap(k) with sₖ error bars and 1-SE k choice; artefact id **`CLU.P.GAP`**; `random_state=42`.
- API `POST /api/v1/unsupervised/clustering/gap` (`n_refs` default 50, 1–200).

## Tests
```
.\.venv\Scripts\python.exe -m ruff check labcore/unsupervised/cluster_plots.py backend/app/routers/unsupervised.py tests/unit/test_cluster_gap.py
# All checks passed!

.\.venv\Scripts\python.exe -m pytest tests/unit/test_cluster_gap.py tests/unit/test_cluster_db.py tests/unit/test_cluster_ch.py tests/unit/test_cluster_elbow.py tests/unit/test_cluster_k_sweep.py tests/unit/test_cluster_silhouette.py tests/unit/test_import_allowlist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 7 items

tests\unit\test_cluster_gap.py .                                         [ 14%]
tests\unit\test_cluster_db.py .                                          [ 28%]
tests\unit\test_cluster_ch.py .                                          [ 42%]
tests\unit\test_cluster_elbow.py .                                       [ 57%]
tests\unit\test_cluster_k_sweep.py .                                     [ 71%]
tests\unit\test_cluster_silhouette.py .                                  [ 85%]
tests\unit\test_import_allowlist.py .                                    [100%]

============================= 7 passed in 38.36s ==============================
```

## Notes
- Seed **42** on numpy Generator, KMeans, and artefact metadata; iris sanity (B=50, k∈2…8): `best_k_1se=3`, Gap ≈ 1.221.
- Distinct from planned c118 **`CLU.P.DENDROGRAM`** (hierarchical/cophenetic) and c117 **`CLU.P.DB`** (Davies–Bouldin k-sweep).
- Next gap: `CLU.P.DENDROGRAM`, `ANO.P.*` beyond SCORE_HIST/RANKED, `FS.P.UNIQUENESS` / `FS.P.HOLDING`, remaining DR plots per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Thin Tibshirani wrapper; sklearn KMeans WCSS only (rule 70).
- [x] Import allowlist green; cluster plot regressions green.