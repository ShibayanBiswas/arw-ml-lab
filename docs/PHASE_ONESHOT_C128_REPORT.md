# Phase oneshot-c128 — ANO.P.PARETO

## Built
- `anomaly_pareto_rank` + thin `_rank_elbow` in `labcore/unsupervised/anomaly_plots.py` — full descending rank–score curve, cumulative % of positive score mass (secondary axis), contamination threshold horizontal line, chord-distance elbow marker; artefact id **`ANO.P.PARETO`**.
- API `POST /api/v1/unsupervised/anomaly/pareto` — fits detector (`fit_anomaly`, seed 42) then returns Pareto rank plot + numbers.

## Tests
```
.\.venv\Scripts\python.exe -m ruff check labcore/unsupervised/anomaly_plots.py backend/app/routers/unsupervised.py tests/unit/test_anomaly_pareto.py
# All checks passed!

.\.venv\Scripts\python.exe -m pytest tests/unit/test_anomaly_pareto.py tests/unit/test_anomaly_ranked.py tests/unit/test_import_allowlist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 5 items

tests\unit\test_anomaly_pareto.py ..                                     [ 40%]
tests\unit\test_anomaly_ranked.py ..                                     [ 80%]
tests\unit\test_import_allowlist.py .                                    [100%]

============================== 5 passed in 18.58s ==============================
```

## Notes
- Seed **42** on API body / `IsolationForest` path.
- Live iris (`n=150`, contamination 0.1): **elbow_rank=29**, **elbow_score≈0.509** (`IsolationForest`, seed 42).
- Distinct from c104 **`ANO.P.RANKED`** (top-N bar only), c126 **`ANO.P.SCORE_HIST`**, c125 **`ANO.P.EMBED`**.
- Next gap: pairwise feature scatter (`ANO.P.*`), `FS.P.SADF` / `FS.P.TRENDSCAN`, remaining DR catalogue plots per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest + live elbow fields from runs.
- [x] Thin wrapper on library scores only (rule 70).
- [x] Import allowlist green; ANO ranked regression green.