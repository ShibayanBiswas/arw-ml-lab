# Phase oneshot-c103 — CLU.P.SILHOUETTE

## Built
- `silhouette_knife` in `labcore/unsupervised/cluster_plots.py` — standardised KMeans labels, `sklearn.metrics.silhouette_samples` ordered per cluster (knife layout), overall mean line; artefact id **`CLU.P.SILHOUETTE`**; `random_state=42`.
- API `POST /api/v1/unsupervised/clustering/silhouette`.

## Tests
```
uv run pytest tests/unit/test_import_allowlist.py tests/unit/test_cluster_silhouette.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 2 items

tests\unit\test_import_allowlist.py .                                    [ 50%]
tests\unit\test_cluster_silhouette.py .                                  [100%]

============================= 2 passed in 12.82s ==============================
```

## Notes
- Seed 42 via KMeans `random_state` and body `seed`.
- Distinct from oneshot-c102 **`DR.P.SCREE`**, c34 **`DR.P.SHEPARD`**, and existing **`CLU.P.K_SWEEP`** (k scan, not per-sample knife).
- Next gap: `FS.P.GRID`, `DR.P.CUMVAR` / biplot, `ANO.P.RANKED`, remaining FS.P.* / CLU·DR·ANO plots per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Thin wrapper; sklearn KMeans + silhouette metrics only (rule 70).
- [x] Import allowlist green.