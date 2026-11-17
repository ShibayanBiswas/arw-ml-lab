# Phase oneshot-c125 — ANO.P.EMBED

## Built
- `anomaly_embedding_scatter` in `labcore/unsupervised/anomaly_plots.py` — standardised PCA 2D scores, inliers (blue scale by score) vs flagged anomalies (red markers); Cohen's *d* score separation; artefact id **`ANO.P.EMBED`**; `random_state=42`.
- API `POST /api/v1/unsupervised/anomaly/embed` — runs `fit_anomaly` then embedding scatter; passes algorithm, contamination, seed 42.

## Tests
```
.\.venv\Scripts\python.exe -m ruff check labcore/unsupervised/anomaly_plots.py backend/app/routers/unsupervised.py tests/unit/test_anomaly_embed.py
# All checks passed!

.\.venv\Scripts\python.exe -m pytest tests/unit/test_anomaly_embed.py tests/unit/test_anomaly_ranked.py tests/unit/test_import_allowlist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 5 items

tests\unit\test_anomaly_embed.py ..                                      [ 40%]
tests\unit\test_anomaly_ranked.py ..                                     [ 80%]
tests\unit\test_import_allowlist.py .                                    [100%]

============================= 5 passed in 22.84s ==============================
```

## Notes
- Seed **42**; Iris IsolationForest (`contamination=0.1`): **n_flagged=15**, PC1/PC2 variance **72.96% / 22.85%**, Cohen's *d* **2.462** (live run).
- Distinct from c124 **`CLU.P.K_DISTANCE`** (DBSCAN eps knee), c104 **`ANO.P.RANKED`**, and bundled **`ANO.P.SCORE_HIST`**.
- Next gap: remaining ANO plots (Pareto rank curve, pairwise scatter), `FS.P.MIN_FFD` / SADF / TRENDSCAN, DR residual catalogue gaps per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Thin wrapper over sklearn PCA + Plotly (rule 70).
- [x] Import allowlist green; ANO ranked regression green.