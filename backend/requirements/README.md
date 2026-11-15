# Python requirements (backend + labcore)

* Python **3.12** (shap 0.54 and xgboost 3.4 need ≥ 3.12; ruptures and autogluon need < 3.14).
* Pins are the latest PyPI releases checked on **15 Nov 2026 (IST)**, except where the joint resolution of the worker image forced an older release: numpy 2.4.6 (aeon needs < 2.5), scipy 1.17.1 (aeon needs < 1.18), pandas 2.3.3 (pytorch-tabular needs < 3), ngboost 0.5.11 (0.6.0 caps scikit-learn < 1.7), torchmetrics 1.8.2 (pytorch-tabular needs < 1.9). Details: `docs/GAP_AUDIT.md` §6.
* The composite files were resolved on the box with `uv pip compile` for Python 3.12 / manylinux x86_64 (PyTorch CPU index added). The generated lock files are committed: `api.lock.txt`, `worker-light.lock.txt`, `worker-train.lock.txt` (worker-train + dev). Install from the lock files; re-run `uv pip compile` and commit the new lock whenever a pin changes. Installation itself was not tested on the box — do that in Phase 0.
* Every library is listed in the Library Matrix (`docs/ARCHITECTURE.md` §44) with licence and purpose. Do not add a library that is not in the matrix without updating it (rule `.cursor/rules/70-use-established-libraries.mdc`).
* PyTorch: install CPU wheels on Render (`--extra-index-url https://download.pytorch.org/whl/cpu`); GPU wheels only on the optional external GPU worker.
* `ml-for-trading` (TradingLab) is a private repository: install it from Git with a deploy key (`pip install "tradinglab @ git+ssh://git@github.com/ShibayanBiswas/ml-for-trading.git@<tag>"`); it is not on PyPI and is not pinned here.

| File | Installed in | Contents |
|---|---|---|
| `api.txt` | `lab-api` (Render web) | FastAPI, Supabase, Celery client, OpenAI-compatible client, pydantic, slowapi (rate limits), OpenTelemetry (FastAPI + Celery tracing) |
| `ml-core.txt` | both workers | numpy/pandas/polars/scipy, scikit-learn, GBMs, NGBoost, quantile-forest, glum, imbalanced-learn, category_encoders, feature-engine, skrub, statsmodels, Optuna (+ integration), evaluation and statistics (mlxtend, MLstatkit, scikit-posthocs, model-diagnostics, scikit-plots, probatus), plotting; Prediction Studio and exports: openpyxl, python-calamine, defusedxml, skops, charset-normalizer, nbformat, WeasyPrint (needs Pango in the image), python-pptx, python-docx |
| `eda.txt` | `lab-worker-light` | sweetviz (comparison report), missingno, phik, dython, dcor, nolds, pandera (data contracts); **no ydata-profiling** (isolated, see below) |
| `ts.txt` | `lab-worker-train` | Nixtla stack (statsforecast, mlforecast, neuralforecast, hierarchicalforecast, utilsforecast, coreforecast), sktime, skforecast, darts, pmdarima, prophet, arch, tsfresh, tsfel, aeon, tslearn, stumpy, ruptures, PyWavelets |
| `dl-cpu.txt` | `lab-worker-train` | torch (CPU), lightning, torchmetrics, pytorch-tabular, pytorch-forecasting, pytorch-tcn, captum (tsai and pytorch-widedeep removed: conflicts) |
| `unsupervised.txt` | `lab-worker-train` | umap-learn, hdbscan, openTSNE, pacmap, trimap, prince, minisom, kmodes, scikit-fuzzy, pyod, pythresh |
| `xai-uq.txt` | both workers | shap, lime, dice-ml, PyALE, interpret, imodels, dtreeviz, shapiq, MAPIE, crepes, venn-abers, netcal, scoringrules, properscoring, fairlearn, cleanlab |
| `worker-light.txt` | `lab-worker-light` | `-r api.txt -r ml-core.txt -r eda.txt -r xai-uq.txt` |
| `worker-train.txt` | `lab-worker-train` | `-r worker-light.txt -r ts.txt -r dl-cpu.txt -r unsupervised.txt` |
| `optional-automl.txt` | separate image `lab-worker-automl` only | autogluon, h2o (needs Java 17) |
| `optional-foundation.txt` | separate image, off by default | chronos-forecasting, timesfm (uni2ts excluded: needs torch < 2.5) |
| `optional-reports.txt` | separate image, off by default | ydata-profiling (needs numpy < 2.4, scipy < 1.17, matplotlib ≤ 3.10) |
| `optional-monitoring.txt` | separate image, off by default | evidently (needs plotly < 6) |
| `optional-gpu.txt` | external GPU worker only | xlstm, mamba-ssm |
| `optional-licence-review.txt` | **not installed** until legal review | alibi (BSL-1.1), phate (GPL-2.0), kmedoids (GPL-3.0), tabpfn (model-weights licence) |
| `dev.txt` | CI and local | pytest, pytest-cov, hypothesis, ruff, mypy, respx, locust, pandas-stubs, factor-analyzer (GPL-2.0, test oracle only — never imported by `labcore`), jsonschema (feature contracts), pgserver (local DB test harness) |
