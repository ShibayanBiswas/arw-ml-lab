# Phase oneshot-c104 — ANO.P.RANKED

## Built
- `anomaly_ranked_bar` in `labcore/unsupervised/anomaly_plots.py` — top-N row indices by descending anomaly score, horizontal bar chart + percentiles; artefact id **`ANO.P.RANKED`**.
- API `POST /api/v1/unsupervised/anomaly/ranked` — fits detector (`fit_anomaly`, seed 42) then ranks scores; `top_n` request field (default 20).

## Tests
```
uv run pytest tests/unit/test_anomaly_ranked.py tests/unit/test_import_allowlist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 3 items

tests\unit\test_anomaly_ranked.py ..                                     [ 66%]
tests\unit\test_import_allowlist.py .                                    [100%]

============================== 3 passed in 6.54s ==============================
```

## Notes
- Seed 42 via `IsolationForest` / body `seed` on the ranked API path.
- Distinct from oneshot-c103 **`CLU.P.SILHOUETTE`**, c102 **`DR.P.SCREE`**, and **`ANO.P.SCORE_HIST`** (histogram bundled in `fit_anomaly`).
- Next gap: Celery worker `heartbeat_at` writes (OPS-03), `FS.P.GRID`, `DR.P.CUMVAR` / biplot, remaining FS.P.* / CLU·DR plots per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Thin wrapper; sklearn/pyod scores only (rule 70).
- [x] Import allowlist green.