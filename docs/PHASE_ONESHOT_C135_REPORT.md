# Phase oneshot-c135 — ANO.P.PAIRWISE

## Built
- `anomaly_pairwise_feature_scatter` + `_top_features_by_score_corr` in `labcore/unsupervised/anomaly_plots.py` — ranks features by |Pearson r| with anomaly scores (`scipy.stats.pearsonr`), Plotly Express `scatter_matrix` on top-*k* features with inlier vs flagged colouring; artefact id **`ANO.P.PAIRWISE`**.
- API `POST /api/v1/unsupervised/anomaly/pairwise` — fits detector (`fit_anomaly`, seed 42) then returns pairwise matrix; body field `top_features` (2–8, default 4).

## Tests
```
.\.venv\Scripts\python.exe -m ruff check labcore/unsupervised/anomaly_plots.py backend/app/routers/unsupervised.py tests/unit/test_anomaly_pairwise.py
# All checks passed!

.\.venv\Scripts\python.exe -m pytest tests/unit/test_anomaly_pairwise.py tests/unit/test_anomaly_pareto.py tests/unit/test_import_allowlist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 5 items

tests\unit\test_anomaly_pairwise.py ..                                   [ 40%]
tests\unit\test_anomaly_pareto.py ..                                     [ 80%]
tests\unit\test_import_allowlist.py .                                    [100%]

============================== 5 passed in 20.30s ==============================
```

## Notes
- Seed **42** on API body / `IsolationForest` path.
- Live iris (`n=150`, contamination 0.1, `top_k=4`): ranked features `f1,f0,f3,f2` with score correlations `[0.164, 0.072, −0.037, −0.035]`; **Cohen's d≈2.46** (live run).
- Distinct from c128 **`ANO.P.PARETO`**, c125 **`ANO.P.EMBED`** (PCA), c104 **`ANO.P.RANKED`**, and c132 **`FS.P.TRENDSCAN`** (finance suitability).
- Next gap: wire **`ANO.P.PARETO`** in anomaly WB; `DR.P.SHEPARD` in DR WB; remaining CLU.P.* in FE.
- No Contabo changes.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest + live correlations/Cohen's d from runs.
- [x] scipy + plotly only for ranking/rendering (rule 70).
- [x] Import allowlist green; ANO pareto regression green.

**Ship commit:** `fc2a30f`