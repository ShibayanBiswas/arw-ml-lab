# Library gap audit — round 3 (15 Nov 2026, IST)

Scope: compare the whole ARW ML Lab design (`docs/ARCHITECTURE.md` §1–§40) against the catalogues of the popular Python ML libraries, add what was missing, and make sure **every algorithm, encoder, preprocessing step, metric, statistical test, CV scheme, EDA item and plot is backed by a popular, maintained library** (rule `.cursor/rules/70-use-established-libraries.mdc`). Lab code is allowed only as thin wrappers; the WFO, PBO/CSCV and CPCV-path drivers are thin wrappers over TradingLab (`ml-for-trading`), sktime, scikit-learn and `arch` functions.

Detailed results are in ARCHITECTURE **§41** (classification evaluation), **§42** (regression evaluation), **§43** (additions and replacements) and **§44** (Library Matrix). This file is the summary and change log.

## 1. Method

1. Each library's public API and user guide (estimator lists, metric modules, plot modules, splitters, encoders, transformers) was compared with the lab catalogues: §10–§13 (EDA, preprocessing, supervised, CV), §15–§19 (metrics, plots, XAI, unsupervised, time series), §32–§37 (WFO, DL, TS, per-family tables).
2. Each gap was classified as **add** (a maintained library provides it and it matters for tabular/TS users), **re-back** (the design said "lab" or named a stale/conflicting library) or **optional** (no maintained, licence-compatible library; kept off by default with a reason).
3. Every catalogue table in ARCHITECTURE received a **Library** column (39 existing tables / 515 rows tagged, plus the new §41–§43 tables). Tables that already had an Implementation/Library column were edited in place.
4. Versions: the latest PyPI release on 15 Nov 2026 (IST), then a joint resolution of all worker images with `uv pip compile --python-version 3.12` (§6). Licences were taken from PyPI metadata/repository licence files.

Not done: import or install tests of every package (the resolution was checked, not an installation), and runtime verification of every API name — Phase 0/6B acceptance criteria cover that.

## 2. Libraries audited and what the lab uses from them

| Library | Used for in the lab | Gaps found → action (IDs in ARCHITECTURE §43) |
|---|---|---|
| scikit-learn 1.9.1 | core estimators, pipelines, splitters, metrics, calibration, threshold tuning, inspection | added IsotonicRegression (R52), PLSRegression (R53), MultiTask Lasso/ElasticNet (R54), MultiOutputRegressor/RegressorChain (R55), LogisticRegressionCV/RidgeClassifierCV (C36), MultiOutputClassifier/ClassifierChain + native multilabel (C37–C38), `TunedThresholdClassifierCV`/`FixedThresholdClassifier` (C39), semi-supervised (C40), PLS/CCA, NCA, rotated FactorAnalysis, MiniBatchNMF, FeatureAgglomeration (D23–D25, D27–D28), spectral bi/co-clustering (K23), PredefinedSplit (cv.predefined), the full `sklearn.metrics` classification/regression set in §41/§42 |
| XGBoost / LightGBM / CatBoost | GBMs (R33–R35, C21–C23) | already covered; their probabilistic darts wrappers added in F62 |
| statsmodels 0.15 | GLMs, quantile/robust regression, residual tests, influence, state space, McNemar/Cochran Q | added AutoReg, ARDL, Markov switching, dynamic factor, Theta/STLForecast (F55–F59); residual tests and `OLSInfluence` tables (§42.4) |
| sktime 1.3 / aeon 1.6 | forecasters, splitters, TS classifiers | aeon ROCKET family, Catch22, interval forests, DTW k-NN, HIVE-COTE 2 (Q14–Q18); sktime splitters for walk-forward/cut-offs (cv.walk_forward, cv.ts_cutoffs); sktime ensembles (F66) |
| darts 0.48 | forecasting, backtests, anomaly scorers | darts model set (F62), RegressionEnsembleModel (F66), backtests (cv.darts_backtest), anomaly scorers (A23) |
| statsforecast / mlforecast / neuralforecast / hierarchicalforecast / utilsforecast | statistical, ML and neural forecasting, reconciliation, losses | already the default TS stack; rolling-origin CV made explicit (cv.nixtla_cv); Fourier terms re-backed to utilsforecast |
| pmdarima, Prophet, arch | auto-ARIMA, Prophet, GARCH, bootstraps, SPA | pmdarima auto_arima as cross-check (F60); EGARCH/GJR/FIGARCH/HARCH/APARCH and HAR-RV (F61); variance-ratio test re-backed to `arch.unitroot` |
| skforecast | direct/recursive forecasters | explicit forecasters (F64) and backtesting folds (cv.ts_fold) |
| pytorch-tabular 1.2 / pytorch-forecasting 1.8 | tabular DL zoo; TFT/N-HiTS/DeepAR | TabNet re-backed from pytorch-tabnet to pytorch-tabular; pytorch-forecasting backend (F63, Q11); ResNet-MLP/SAINT/DCN-v2 optional (§43.4) |
| umap-learn, hdbscan, openTSNE, pacmap, trimap, prince, tslearn | DR and clustering | densMAP (D26); time-series k-means, k-Shape, kernel k-means (K20–K22) |
| pyod 3 + pythresh, stumpy, ruptures | anomaly detection | INNE, KDE/GMM/MCD/SOD/ROD/LMDD, DIF, LUNAR/ALAD/GAN detectors, XGBOD, LSCP (A15–A20), matrix-profile discords (A21), change points (A22), pythresh thresholding |
| imbalanced-learn | resamplers, balanced ensembles, imbalance metrics | `classification_report_imbalanced`, G-mean, IBA, specificity/sensitivity in §41 (CLE.T.REPORT_IMB) |
| category_encoders, feature-engine, skrub | encoders, imputers, discretisers, outliers, creation, datetime/lag/window, selection | encoders E23–E32; feature-engine imputers, outlier cappers, discretisers, transformers, creation, datetime, TS features and selectors (§43.8); optbinning; pandera contracts |
| ydata-profiling, sweetviz | EDA reports | ydata-profiling isolated (dependency conflict, §6); its alert types reproduced as EDA.T.ALERTS; sweetviz kept for train/test comparison; phik, dython, dcor, nolds, missingno tables/plots (§43.10) |
| yellowbrick | visual diagnostics checklist | last release 2022 → not installed; its plots (discrimination threshold, class prediction error, residuals, Cook's distance, rank1D/2D, RadViz, learning/validation curves, silhouette) are CLE.P / REE.P / EDA.P artefacts computed with sklearn/statsmodels/scipy and drawn with Plotly |
| shap, lime, PyALE, dice-ml, interpret, captum, dtreeviz, shapiq | explanations | alibi ALE → PyALE; SHAP interaction values replace Friedman H as default; captum DL attributions; Anchors optional (BSL-1.1) (§43.11) |
| MAPIE 1.6, crepes, venn-abers, netcal, scoringrules, properscoring | conformal, calibration, scoring rules | Mondrian conformal and predictive systems (crepes), Venn–Abers (C43), beta/histogram/BBQ calibration and ECE family (netcal), CRPS/energy/interval scores |
| Optuna 5 + optuna-integration | tuning and its plots | QMC/BruteForce/NSGA-III/GP samplers, extra pruners, all `optuna.visualization` plots, RDB storage on Supabase Postgres |
| mlxtend, MLstatkit, scikit-posthocs, model-diagnostics, scikit-plots, fairlearn, cleanlab, iterative-stratification | evaluation statistics, plots and CV | 5×2cv t/F and .632+ bootstrap (mlxtend), GroupTimeSeriesSplit (cv.group_ts), DeLong (MLstatkit), Nemenyi/CD diagrams, Murphy decomposition, gains/lift/KS, MetricFrame slices, label issues, multilabel stratified K-fold (cv.multilabel_strat) |
| imodels, gplearn, glum, quantile-forest, gpboost, wittgenstein | interpretable / specialised models | FIGS/HSTree (R59), RuleFit/FIGS/rule lists (C41), symbolic regression (R58, optional), glum GLMs (R57), quantile regression forest (R56), GPBoost (R60, optional), RIPPER (C42, optional) |
| PyCaret 3.3.2, H2O, AutoGluon | AutoML | PyCaret used as a coverage checklist only (last release April 2024, old pins); AutoGluon and H2O presets in the separate optional AutoML image (R61/C44, R62/C45, F65) |

## 3. Additions (counts; IDs in ARCHITECTURE §43)

| Catalogue | Before | Added | After |
|---|---|---|---|
| Regression algorithms | 51 | 11 (R52–R62) | 62 |
| Classification algorithms | 35 | 10 (C36–C45) | 45 |
| Sequential window models | 13 | 5 (Q14–Q18) | 18 |
| Dimensionality reduction | 22 | 6 (D23–D28) | 28 |
| Clustering | 19 | 4 (K20–K23) | 23 |
| Anomaly detection | 14 | 9 (A15–A23) + pythresh thresholding | 23 |
| Forecasting | 54 | 13 (F55–F67) | 67 |
| Encoders | 22 | 10 (E23–E32) | 32 |
| CV schemes | 20 + purged/CPCV | 9 new keys, 3 re-backed | 29 |
| Classification evaluation (§41) | 25 metrics / 9 tables / 13 plots | full suite | **55 metrics / 42 tables / 45 plots**, 13 threshold methods, 11 statistical tests, 8 AI templates |
| Regression evaluation (§42) | 22 metrics / 8 tables / 16 plots | full suite | **40 metrics / 17 tables / 36 plots**, 6 AI templates |
| EDA | 19 tables / 9 plot groups | 7 tables, 6 plots | 26 tables |
| Preprocessing / selection, XAI / UQ / tuning | — | §43.8, §43.11 | — |

## 4. Replacements and re-backing (cells that said "lab" or named a problem library)

| Where | Before | After |
|---|---|---|
| §11.2/§11.5 mRMR | "mRMR" (no library) | `feature_engine.selection.MRMR` |
| §11.3 lags & differences | lab `shift(k)` | pandas / `feature_engine.timeseries.forecasting.LagFeatures` |
| §12 R41/C29 greedy ensemble | lab | sklearn Stacking/Voting; Caruana selection = optional thin wrapper |
| §12 R45 ResNet-MLP, §34.3 T2 / T6 SAINT / T9 DCN-v2 | rtdl / lab | optional, off by default (no maintained library compatible with numpy 2 / scikit-learn 1.9) |
| §12 R46 / C34 TabNet, §34.3 T3 | pytorch-tabnet (last release 2023) | pytorch-tabular `TabNetModelConfig` |
| §13.1 cv.bootstrap | lab | `mlxtend.evaluate.bootstrap_point632_score` |
| §13.1 cv.walk_forward | lab | `sktime.split.ExpandingWindowSplitter` / `SlidingWindowSplitter` (thin WFO driver) |
| §13.1 cv.blocked | lab | sklearn `KFold(shuffle=False)` + thin gap wrapper |
| §13.1 cv.hv_block | lab | optional thin wrapper (no maintained library) |
| §13.1 cv.nested | lab wrapper | sklearn `cross_validate` over a search object (thin) |
| §17 ALE | alibi / PyALE | PyALE (alibi BSL-1.1 not used) |
| §17 Friedman H | lab / sklearn PDP | shap interaction values by default; H optional thin wrapper |
| §17 Anchors | alibi | optional, off until licensed |
| §18.1 PHATE | phate | licence review (GPL-2.0); TriMap/PaCMAP kept |
| §18.2 K-Medoids | scikit-learn-extra / kmedoids | optional (kmedoids GPL-3.0; scikit-learn-extra last released 2023) |
| §18.3 A2 Extended IF | pyod / isotree | `pyod` IForest / DIF |
| §18.3 A9 PCA reconstruction | pyod / lab | `pyod.models.pca.PCA` |
| §18.3 A13 Mahalanobis | lab | `sklearn.covariance.MinCovDet` / `pyod` MAD |
| §18.3 A14 TS anomalies | lab / statsmodels | statsmodels STL + pyod MAD; S-H-ESD optional thin |
| §19.1 Hurst, variance ratio | lab | `nolds` Hurst / `arch.unitroot.VarianceRatio` |
| §19.1 differencing preview | lab | pandas / scipy Box-Cox / coreforecast Guerrero / TradingLab FFD |
| §19.2 F13 Fourier terms | lab Fourier | `utilsforecast.feature_engineering.fourier` |
| §19.2 F26 Kalman | statsmodels / pykalman | statsmodels state space / darts KalmanForecaster (pykalman conflicts with sktime) |
| §19.2 F54 ensembles | lab | sktime EnsembleForecaster / darts RegressionEnsembleModel |
| §32 bet resampling, random-entry benchmark | lab | thin wrappers over TradingLab bets + `numpy.random.Generator` |
| §34 DL.P.ARCH | lab SVG | lightning `ModelSummary` → SVG |
| §35.3 DirRec / DIRMO / Rectify | lab | thin wrappers over skforecast / mlforecast / sklearn MultiOutputRegressor |
| §36.1 / §36.2 | REG.T.* / CLF.T.* | superseded by REE.* (§42) and CLE.* (§41); old IDs kept as aliases |
| §41 DeLong | confidenceinterval | MLstatkit (confidenceinterval pins setuptools ~= 68.2) |
| §41 Nadeau–Bengio corrected t | mlxtend | thin wrapper over `scipy.stats.t` (mlxtend has no such function) |
| §42 Huber loss | torchmetrics | thin numpy formula (no torchmetrics Huber metric) |
| §42 interval score | sktime PinballLoss | `scoringrules.interval_score` |
| §4 tech stack | alibi, scikit-learn-extra, kmedoids | PyALE, dice-ml, pyod + pythresh, tslearn; optional K-Medoids |
| §43.10 MIC | minepy | removed (GPL, unmaintained); distance correlation (dcor) and phik instead |

## 5. Licence and maintenance flags

* **Not imported by labcore:** alibi, alibi-detect (BSL-1.1); PHATE (GPL-2.0); kmedoids (GPL-3.0); pycatch22 (GPL-3.0); minepy, pingouin (GPL); deepchecks (AGPL-3.0); sdv/deepecho (BUSL); scikit-survival (GPL-3.0). `factor-analyzer` (GPL-2.0) only in `dev.txt` as a test oracle for KMO/Bartlett.
* **TabPFN:** package Apache-2.0, recent model weights non-commercial → off.
* **Stale but kept (optional or only option):** lime (last release 2020; kept because the design requires LIME and it still works with current numpy), kmodes (2022, optional), scikit-fuzzy (low cadence, optional), PyCaret (checklist only), neuralprophet and adtk not used, yellowbrick not installed (plots recreated from library numbers), rtdl and pytorch-tabnet not used.
* **LGPL:** psycopg (dynamic use, allowed).

## 6. Dependency resolution (Python 3.12, `uv pip compile`, manylinux x86_64, PyTorch CPU index)

All composites resolve (re-resolved 15 Nov 2026 after the round-4 additions — Prediction Studio, hardening and report exports): `api.txt` (85 pinned packages in the lock), `worker-light.txt` + `dev.txt` (362), `worker-train.txt` + `dev.txt` (424). Conflicts found and how they were fixed:

| Conflict | Fix |
|---|---|
| aeon 1.6 needs numpy < 2.5 and scipy < 1.18 | numpy 2.4.6, scipy 1.17.1 |
| pytorch-tabular 1.2 needs pandas < 3 and torchmetrics < 1.9 (without the pandas pin uv back-tracked to pytorch-tabular 0.7.0, which fails to build) | pandas 2.3.3, torchmetrics 1.8.2 |
| ngboost 0.6.0 caps scikit-learn < 1.7 | ngboost 0.5.11 |
| confidenceinterval 1.0.5 pins setuptools ~= 68.2 | replaced by MLstatkit 0.1.91 |
| pykalman 0.11.2 needs scikit-base < 0.14 (sktime 1.3 needs ≥ 1.0) | removed |
| tsai 1.0.1 needs scikit-learn < 1.8 | removed |
| pytorch-widedeep 1.7.0 needs numpy < 2 | removed |
| ydata-profiling 4.18.4 needs numpy < 2.4, scipy < 1.17, matplotlib ≤ 3.10 | `optional-reports.txt` (separate image) |
| evidently 0.7.23 needs plotly < 6 | `optional-monitoring.txt` (separate image) |
| uni2ts 2.0.0 needs torch < 2.5 | excluded |
| PyWavelets 1.10.0 (`ts.txt`) and wittgenstein 0.3.5 (`xai-uq.txt`) added late in the audit | resolved, no other pin moved |

## 7. Optional / off by default (with reasons)

T2 ResNet-MLP, T6 SAINT, T9 DCN-v2, T13 (no compatible maintained library); DEC and autoencoder DR (no maintained tabular library; can be composed from torch.nn later); K-Medoids (licence/maintenance); fuzzy c-means and k-modes/k-prototypes (low release cadence); PHATE and Anchors (licence); S-H-ESD, hv-block CV and Friedman H (thin wrappers, no library); R58 symbolic regression, R60 GPBoost, C40, C42 (niche; see §43.2); AutoML (AutoGluon, H2O) and foundation forecasters (Chronos, TimesFM) in separate images; xLSTM/Mamba on the external GPU worker only.

## 8. Files changed in round 3

New: `docs/GAP_AUDIT.md`, `.cursor/rules/70-use-established-libraries.mdc`, `backend/requirements/` (README.md, 16 requirement files, 3 lock files), `docs/diagrams/19_classification_eval.png`, `docs/diagrams/src/19_classification_eval.mmd`.

Updated: `docs/ARCHITECTURE.md` (v2.1: §41–§44 appended, Library columns, pointers in §12/§15/§16/§36, counts in §36.8, VD11 in §38, re-backed cells), `CURSOR_PROMPT.md`, `AGENTS.md`, `README.md`, `docs/FLOWCHART.md`, `.cursor/rules/01-stack.mdc`, `.cursor/rules/20-ml-integrity.mdc`, `.cursor/rules/30-testing.mdc`, `docs/plans/build_plan_page.tsx`.
