# Phase oneshot-c126 — ANO.P.SCORE_HIST

## Built
- `anomaly_score_hist` in `labcore/unsupervised/anomaly_plots.py` — overlaid inlier vs flagged histograms, contamination threshold vline, Cohen's *d* separation and `n_above_threshold` in numbers JSON; artefact id **`ANO.P.SCORE_HIST`**.
- `fit_anomaly` passes `is_outlier` into the bundled score-hist artefact.
- API `POST /api/v1/unsupervised/anomaly/score-hist` — runs `fit_anomaly` then returns the histogram artefact; seed 42 via body `seed`.

## Tests
```
.\.venv\Scripts\python.exe -m ruff check labcore/unsupervised/anomaly_plots.py labcore/unsupervised/anomaly.py backend/app/routers/unsupervised.py tests/unit/test_anomaly_score_hist.py
# All checks passed!

.\.venv\Scripts\python.exe -m pytest tests/unit/test_anomaly_score_hist.py tests/unit/test_anomaly_embed.py tests/unit/test_anomaly_ranked.py tests/unit/test_import_allowlist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 8 items

tests\unit\test_anomaly_score_hist.py ...                                [ 37%]
tests\unit\test_anomaly_embed.py ..                                      [ 62%]
tests\unit\test_anomaly_ranked.py ..                                     [ 87%]
tests\unit\test_import_allowlist.py .                                    [100%]

============================= 8 passed in 14.26s ==============================
```

## Notes
- Seed **42**; Iris IsolationForest (`contamination=0.1`): **n_flagged=15**, threshold **0.5367**, Cohen's *d* **2.462** (live run).
- Distinct from c125 **`ANO.P.EMBED`** (PCA scatter), c104 **`ANO.P.RANKED`** (top-N bar), and §36 Pareto rank curve (next gap).
- Next gap: Pareto rank curve, pairwise feature scatter, `FS.P.MIN_FFD` / SADF / TRENDSCAN, DR residual catalogue gaps per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Thin wrapper over sklearn/pyod scores + Plotly (rule 70).
- [x] Import allowlist green; ANO embed/ranked regression green.