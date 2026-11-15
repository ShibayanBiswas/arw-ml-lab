import {
  Page, Section, Text, Table, Metrics, Diagram, Sequence, Grid, Callout, Segmented, NumberedList,
  TableOfContents, Properties, useState, useMemo,
} from "grok/canvas";

type Fam = "R" | "C" | "S" | "D" | "K" | "A" | "F";

const ALGOS: Record<Fam, [string, string, string][]> = {"R":[["R1","Linear Regression (OLS)","sklearn"],["R2","Ridge","sklearn"],["R3","Lasso","sklearn"],["R4","ElasticNet","sklearn"],["R5","Lars / LassoLars","sklearn"],["R6","Orthogonal Matching Pursuit","sklearn"],["R7","Bayesian Ridge","sklearn"],["R8","ARD Regression","sklearn"],["R9","Huber","sklearn"],["R10","RANSAC","sklearn"],["R11","Theil-Sen","sklearn"],["R12","Quantile Regression","sklearn"],["R13","Poisson / Gamma / Tweedie GLM","sklearn"],["R14","SGD Regressor","sklearn"],["R15","Passive-Aggressive","sklearn"],["R16","Polynomial + Ridge","sklearn"],["R17","Spline GAM","pygam / sklearn SplineTransformer+Ridge"],["R18","KNN Regressor","sklearn"],["R19","Radius Neighbors","sklearn"],["R20","SVR","sklearn"],["R21","Linear SVR","sklearn"],["R22","Nu-SVR","sklearn"],["R23","Kernel Ridge","sklearn"],["R24","Gaussian Process","sklearn"],["R25","Decision Tree","sklearn"],["R26","Extra Tree (single)","sklearn"],["R27","Random Forest","sklearn"],["R28","Extra Trees","sklearn"],["R29","Bagging","sklearn"],["R30","AdaBoost","sklearn"],["R31","Gradient Boosting","sklearn"],["R32","Hist Gradient Boosting","sklearn"],["R33","XGBoost","xgboost"],["R34","LightGBM","lightgbm"],["R35","CatBoost","catboost"],["R36","NGBoost","ngboost"],["R37","Explainable Boosting Machine","interpret"],["R38","RuleFit","imodels"],["R39","Stacking","sklearn"],["R40","Voting","sklearn"],["R41","Blending / greedy ensemble selection (Caruana)","sklearn Stacking / Voting (greedy = optional thin wrapper)"],["R42","Sequentially bootstrapped bagging (sequential)","TradingLab ensemble/sb_bagging.py"],["R43","MLP (sklearn)","sklearn"],["R44","MLP (PyTorch)","PyTorch Lightning"],["R45","ResNet-MLP (tabular)","optional, off (no maintained library)"],["R46","TabNet","pytorch-tabular (TabNetModelConfig)"],["R47","FT-Transformer","pytorch-tabular"],["R48","TabTransformer","pytorch-tabular"],["R49","NODE","pytorch-tabular"],["R50","GANDALF / GATE / AutoInt / DANet","pytorch-tabular"],["R51","TabPFN (10k rows, 500 features max)","tabpfn"],["R52","Isotonic regression","sklearn.isotonic.IsotonicRegression"],["R53","PLS regression","sklearn.cross_decomposition.PLSRegression"],["R54","Multi-task Lasso / ElasticNet","sklearn.linear_model.MultiTaskLassoCV / MultiTaskElasticNetCV"],["R55","Multi-output wrappers","sklearn.multioutput.MultiOutputRegressor, RegressorChain"],["R56","Quantile regression forest","quantile_forest.RandomForestQuantileRegressor"],["R57","GLM (glum)","glum.GeneralizedLinearRegressorCV"],["R58","Symbolic regression (optional, Thorough)","gplearn.genetic.SymbolicRegressor"],["R59","FIGS / hierarchical-shrinkage trees","imodels (FIGSRegressor, HSTreeRegressorCV)"],["R60","GPBoost (boosting + random effects) (optional)","gpboost"],["R61","AutoML preset (optional image)","autogluon.tabular.TabularPredictor"],["R62","AutoML preset (optional image, Java 17)","h2o.automl.H2OAutoML"]],"C":[["C1","Logistic Regression","sklearn"],["C2","Ridge Classifier","sklearn"],["C3","SGD Classifier","sklearn"],["C4","Perceptron / Passive-Aggressive","sklearn"],["C5","LDA","sklearn"],["C6","QDA","sklearn"],["C7","Gaussian NB","sklearn"],["C8","Multinomial / Complement / Bernoulli / Categorical NB","sklearn"],["C9","KNN","sklearn"],["C10","Nearest Centroid / Radius NN","sklearn"],["C11","SVC","sklearn"],["C12","Linear SVC / Nu-SVC","sklearn"],["C13","Gaussian Process Classifier","sklearn"],["C14","Decision Tree","sklearn"],["C15","Random Forest","sklearn"],["C16","Extra Trees","sklearn"],["C17","Bagging","sklearn"],["C18","AdaBoost","sklearn"],["C19","Gradient Boosting","sklearn"],["C20","Hist Gradient Boosting","sklearn"],["C21","XGBoost","xgboost"],["C22","LightGBM","lightgbm"],["C23","CatBoost","catboost"],["C24","NGBoost Classifier","ngboost"],["C25","EBM","interpret"],["C26","Balanced RF / EasyEnsemble / RUSBoost / BalancedBagging","imbalanced-learn"],["C27","Stacking","sklearn"],["C28","Voting","sklearn"],["C29","Greedy ensemble selection","sklearn Stacking / Voting (greedy = optional thin wrapper)"],["C30","One-vs-Rest / One-vs-One / Output-Code wrappers","sklearn"],["C31","Sequentially bootstrapped bagging (sequential)","TradingLab SequentiallyBootstrappedBaggingClassifier"],["C32","Calibrated wrapper","sklearn CalibratedClassifierCV"],["C33","MLP (sklearn / PyTorch)","sklearn / Lightning"],["C34","ResNet, TabNet, FT-Transformer, TabTransformer, NODE, GANDALF, AutoInt","pytorch-tabular (ResNet optional)"],["C35","TabPFN Classifier","tabpfn"],["C36","Logistic / Ridge classifier with built-in CV","sklearn.linear_model.LogisticRegressionCV, RidgeClassifierCV"],["C37","Multilabel wrappers","sklearn.multioutput.MultiOutputClassifier, ClassifierChain"],["C38","Native multilabel estimators","sklearn RandomForestClassifier, ExtraTreesClassifier, KNeighborsClassifier, MLPClassifier"],["C39","Threshold wrappers","sklearn.model_selection.TunedThresholdClassifierCV, FixedThresholdClassifier"],["C40","Semi-supervised (optional)","sklearn.semi_supervised.SelfTrainingClassifier, LabelSpreading"],["C41","Interpretable rule models","imodels (RuleFitClassifier, FIGSClassifier, GreedyRuleListClassifier)"],["C42","RIPPER rule learner (optional)","wittgenstein.RIPPER"],["C43","Calibrated prediction sets","venn_abers.VennAbersCalibrator"],["C44","AutoML preset (optional image)","autogluon.tabular.TabularPredictor"],["C45","AutoML preset (optional image, Java 17)","h2o.automl.H2OAutoML"]],"S":[["S1","Any regression/classification model on engineered lag/rolling features","sklearn / GBMs"],["S2","Vanilla RNN (Elman)","torch.nn + lightning"],["S3","LSTM","torch.nn + lightning"],["S4","GRU","torch.nn + lightning"],["S5","Stacked / attention LSTM","torch.nn + lightning"],["S6","1D-CNN","torch.nn + lightning"],["S7","TCN (dilated causal conv)","pytorch-tcn + lightning"],["S8","CNN-LSTM hybrid","torch.nn + lightning"],["S9","Transformer encoder (causal mask)","torch.nn + lightning"],["S10","xLSTM / Mamba-style SSM (optional)","xlstm / mamba-ssm (optional GPU)"],["S11","Sequentially bootstrapped bagging","TradingLab"]],"D":[["D1","PCA","sklearn"],["D2","Incremental PCA","sklearn"],["D3","Kernel PCA","sklearn"],["D4","Sparse PCA / MiniBatch Sparse PCA","sklearn"],["D5","Truncated SVD","sklearn"],["D6","Factor Analysis","sklearn"],["D7","FastICA","sklearn"],["D8","NMF","sklearn"],["D9","Dictionary Learning","sklearn"],["D10","LDA (supervised DR)","sklearn"],["D11","Gaussian / Sparse Random Projection","sklearn"],["D12","t-SNE","sklearn / openTSNE"],["D13","UMAP","umap-learn"],["D14","Isomap","sklearn"],["D15","LLE (standard, modified, Hessian, LTSA)","sklearn"],["D16","Spectral Embedding","sklearn"],["D17","Metric / non-metric / classical MDS","sklearn"],["D18","PHATE / TriMap / PaCMAP (optional)","trimap / pacmap; phate licence review"],["D19","MCA / FAMD (categorical / mixed)","prince"],["D20","Autoencoder (dense)","optional: torch.nn + lightning"],["D21","Variational Autoencoder","optional: torch.nn + lightning"],["D22","Denoising / Sparse Autoencoder","optional: torch.nn + lightning"],["D23","PLS / CCA (supervised DR)","sklearn.cross_decomposition"],["D24","Neighbourhood components analysis","sklearn.neighbors.NeighborhoodComponentsAnalysis"],["D25","Factor analysis with varimax / quartimax rotation","sklearn.decomposition.FactorAnalysis(rotation=…)"],["D26","densMAP","umap.UMAP(densmap=True)"],["D27","Mini-batch NMF","sklearn.decomposition.MiniBatchNMF"],["D28","Feature agglomeration (variable clustering)","sklearn.cluster.FeatureAgglomeration"]],"K":[["K1","K-Means","sklearn"],["K2","Mini-Batch K-Means","sklearn"],["K3","Bisecting K-Means","sklearn"],["K4","K-Medoids (PAM / CLARA)","optional: kmedoids (GPL) / scikit-learn-extra"],["K5","K-Modes / K-Prototypes","kmodes"],["K6","Fuzzy C-Means","scikit-fuzzy"],["K7","Agglomerative (hierarchical)","sklearn + scipy"],["K8","BIRCH","sklearn"],["K9","DBSCAN","sklearn"],["K10","HDBSCAN","sklearn / hdbscan"],["K11","OPTICS","sklearn"],["K12","Mean Shift","sklearn"],["K13","Affinity Propagation","sklearn"],["K14","Spectral Clustering","sklearn"],["K15","Gaussian Mixture","sklearn"],["K16","Bayesian GMM (Dirichlet process)","sklearn"],["K17","ONC (Optimal Number of Clusters)","TradingLab clustering/onc.py"],["K18","Self-Organising Map","MiniSom"],["K19","Deep Embedded Clustering (DEC)","optional: torch.nn + sklearn"],["K20","Time-series k-means (Euclidean / DTW / soft-DTW)","tslearn.clustering.TimeSeriesKMeans"],["K21","k-Shape","tslearn.clustering.KShape"],["K22","Kernel k-means","tslearn.clustering.KernelKMeans"],["K23","Spectral bi-/co-clustering (optional)","sklearn.cluster.SpectralBiclustering, SpectralCoclustering"]],"A":[["A1","Isolation Forest","sklearn"],["A2","Extended Isolation Forest","pyod (IForest / DIF)"],["A3","Local Outlier Factor (novelty)","sklearn"],["A4","One-Class SVM / SGD-OCSVM","sklearn"],["A5","Elliptic Envelope (MCD)","sklearn"],["A6","COPOD / ECOD","pyod"],["A7","HBOS","pyod"],["A8","KNN / average-KNN detector","pyod"],["A9","PCA reconstruction error","pyod.models.pca"],["A10","Autoencoder / VAE detector","pyod / PyTorch"],["A11","Deep SVDD","pyod"],["A12","LODA, CBLOF, Feature Bagging, SUOD","pyod"],["A13","Mahalanobis / robust z","sklearn MinCovDet / pyod MAD"],["A14","Time-series anomalies (STL residual z, S-H-ESD, rolling z)","statsmodels STL + pyod MAD; S-H-ESD optional thin"],["A15","INNE","pyod.models.inne"],["A16","KDE / GMM / MCD / SOD / ROD / LMDD detectors","pyod.models.*"],["A17","Deep Isolation Forest","pyod.models.dif"],["A18","LUNAR, ALAD, AnoGAN, SO-GAAL / MO-GAAL (optional, GPU)","pyod.models.*"],["A19","XGBOD (semi-supervised, uses known anomalies)","pyod.models.xgbod"],["A20","LSCP ensemble","pyod.models.lscp"],["A21","Matrix-profile discords (time series)","stumpy.stump"],["A22","Change points (PELT, BinSeg, BottomUp, Window, KernelCPD)","ruptures"],["A23","Darts anomaly scorers (k-means, norm, Wasserstein)","darts.ad"]],"F":[["F1","Naive (random walk)","statsforecast"],["F2","Seasonal Naive","statsforecast"],["F3","Random Walk with Drift","statsforecast"],["F4","Historic / Window / Seasonal Window Average","statsforecast"],["F5","Simple Exponential Smoothing","statsforecast / statsmodels"],["F6","Holt (linear, damped)","statsmodels / statsforecast"],["F7","Holt-Winters","statsmodels / statsforecast"],["F8","ETS state-space / AutoETS","statsforecast / statsmodels"],["F9","ARIMA","statsmodels / statsforecast"],["F10","SARIMA","statsmodels SARIMAX"],["F11","SARIMAX (exogenous)","statsmodels"],["F12","Auto-ARIMA","statsforecast AutoARIMA"],["F13","ARIMA with Fourier terms","statsforecast + utilsforecast fourier"],["F14","Theta family / AutoTheta","statsforecast"],["F15","Complex Exponential Smoothing","statsforecast"],["F16","TBATS / BATS","statsforecast"],["F17","MSTL + trend forecaster","statsforecast"],["F18","MFLES / AutoMFLES","statsforecast"],["F19","Unobserved Components (UCM)","statsmodels"],["F20","Prophet","prophet"],["F21","VAR","statsmodels"],["F22","VARMAX","statsmodels"],["F23","VECM","statsmodels"],["F24","GARCH / ARCH family","arch / statsforecast"],["F25","Croston / SBA / ADIDA / IMAPA / TSB","statsforecast"],["F26","Kalman filter / local level","statsmodels / darts Kalman"],["F27","ML with lag features (direct / recursive)","mlforecast"],["F28","sktime / skforecast reduction","sktime / skforecast"],["F29","RNN","neuralforecast"],["F30","LSTM","neuralforecast"],["F31","GRU","neuralforecast"],["F32","Dilated RNN","neuralforecast"],["F33","xLSTM","neuralforecast"],["F34","TCN","neuralforecast"],["F35","BiTCN","neuralforecast"],["F36","DeepAR","neuralforecast"],["F37","DeepNPTS","neuralforecast"],["F38","MLP / MLPMultivariate","neuralforecast"],["F39","N-BEATS","neuralforecast"],["F40","N-BEATSx","neuralforecast"],["F41","N-HiTS","neuralforecast"],["F42","DLinear / NLinear","neuralforecast"],["F43","TiDE","neuralforecast"],["F44","Temporal Fusion Transformer","neuralforecast"],["F45","Vanilla Transformer","neuralforecast"],["F46","Informer","neuralforecast"],["F47","Autoformer / FEDformer","neuralforecast"],["F48","PatchTST","neuralforecast"],["F49","iTransformer","neuralforecast"],["F50","TimesNet","neuralforecast"],["F51","TSMixer / TimeMixer / SOFTS / TimeXer / StemGNN / KAN","neuralforecast"],["F52","Auto* versions of every neural model","neuralforecast (Optuna / Ray)"],["F53","Foundation zero-shot (Chronos-Bolt / TimesFM / Moirai)","open weights, optional"],["F54","Ensembles / combinations","sktime EnsembleForecaster / darts ensembles"],["F55","AutoReg AR(p)","statsmodels.tsa.ar_model.AutoReg"],["F56","ARDL / UECM","statsmodels.tsa.ardl"],["F57","Markov-switching regression / AR (regimes)","statsmodels.tsa.regime_switching"],["F58","Dynamic factor model (incl. mixed frequency)","statsmodels.tsa.statespace.DynamicFactor, DynamicFactorMQ"],["F59","ThetaModel, STLForecast (alternative backends)","statsmodels.tsa.forecasting"],["F60","pmdarima auto_arima","pmdarima.auto_arima"],["F61","GARCH family: EGARCH, GJR, FIGARCH, HARCH, APARCH; HAR-RV","arch.arch_model"],["F62","Darts models: Kalman, FFT, TSMixer, TiDE, BlockRNN, probabilistic GBMs","darts.models"],["F63","pytorch-forecasting TFT / N-HiTS / DeepAR","pytorch_forecasting"],["F64","skforecast ForecasterRecursive / ForecasterDirect / ForecasterRecursiveMultiSeries","skforecast"],["F65","AutoGluon TimeSeriesPredictor (optional image)","autogluon.timeseries"],["F66","Forecast ensembles","sktime EnsembleForecaster / darts RegressionEnsembleModel"],["F67","Foundation models (optional image): Chronos, TimesFM","chronos-forecasting, timesfm"]]};

const FAM_OPTS: { value: Fam; label: string }[] = [
  { value: "R", label: "Regression" },
  { value: "C", label: "Classification" },
  { value: "S", label: "Sequential DL" },
  { value: "D", label: "Dim. reduction" },
  { value: "K", label: "Clustering" },
  { value: "A", label: "Anomaly" },
  { value: "F", label: "Forecasting" },
];

const DATASETS: string[][] = [
  ["DS1", "Iris", "Classification (3 classes)", "class", "UCI", "Downloaded"],
  ["DS2", "Breast Cancer WDBC", "Binary", "diagnosis", "UCI", "Downloaded"],
  ["DS3", "Titanic", "Binary, mixed + missing", "Survived", "GitHub / OpenML 40945", "Downloaded"],
  ["DS4", "Adult Census Income", "Binary, imbalance", "income", "UCI", "URL verified"],
  ["DS5", "German Credit (credit-g)", "Binary, cost-sensitive", "class", "OpenML 31", "URL verified"],
  ["DS6", "Credit Card Fraud", "Binary, 0.17% positive", "Class", "OpenML 1597", "URL verified"],
  ["DS7", "Bank Marketing", "Binary, categorical-heavy", "y", "UCI 222", "URL verified"],
  ["DS8", "Default of Credit Card Clients", "Binary, finance", "default", "UCI 350", "URL verified"],
  ["DS9", "Heart Disease (Cleveland)", "Binary / multiclass", "num", "UCI 45", "Downloaded"],
  ["DS10", "Palmer Penguins", "Multiclass; clustering", "species", "seaborn-data", "Downloaded"],
  ["DS11", "Wine Quality (red)", "Regression / ordinal", "quality", "UCI", "Downloaded"],
  ["DS12", "California Housing", "Regression", "median_house_value", "OpenML 537", "URL verified"],
  ["DS13", "Ames House Prices", "Regression, 80 cols", "SalePrice", "OpenML 42165", "URL verified"],
  ["DS14", "Auto MPG", "Regression, small", "mpg", "UCI 9", "Downloaded"],
  ["DS15", "Concrete Strength", "Regression, non-linear", "strength", "UCI 165", "Downloaded"],
  ["DS16", "Bike Sharing", "Count regression; TS + exog", "cnt", "UCI 275", "Downloaded"],
  ["DS17", "Diabetes / Digits / Wine", "sklearn built-ins", "—", "bundled", "Bundled"],
  ["DS18", "Mall Customers", "Clustering", "—", "GitHub", "Downloaded"],
  ["DS19", "Wholesale Customers", "Clustering + anomaly", "—", "UCI", "Downloaded"],
  ["DS20", "Online Retail II", "RFM segmentation", "—", "UCI 502", "URL verified"],
  ["DS21", "Credit Card Fraud (unlabelled)", "Anomaly detection", "hidden", "OpenML 1597", "URL verified"],
  ["DS22", "Airline Passengers", "TS monthly, m=12", "Passengers", "GitHub", "Downloaded"],
  ["DS23", "Shampoo Sales", "TS short (36)", "Sales", "GitHub", "Downloaded"],
  ["DS24", "Daily Min Temperatures", "TS daily", "Temp", "GitHub", "Downloaded"],
  ["DS25", "Monthly Sunspots", "TS long cycle", "Sunspots", "GitHub", "Downloaded"],
  ["DS26", "Mauna Loa CO2", "TS trend + season", "average", "NOAA GML", "Downloaded"],
  ["DS27", "US Macrodata", "Multivariate TS (VAR)", "realgdp", "statsmodels", "Downloaded"],
  ["DS28", "ETTh1", "Multivariate hourly DL", "OT", "ETDataset", "Downloaded"],
  ["DS29", "Electricity Load 2011-14", "Global multi-series", "per client", "UCI 321", "URL verified"],
  ["DS30", "NIFTY 50 daily, 5 years", "Financial sequential", "fwd return / barrier label", "Yahoo chart API", "Downloaded"],
  ["DS31", "S&P 500, NIFTY constituents", "Multi-asset / portfolio", "—", "Yahoo chart API", "URL verified"],
  ["DS32", "TradingLab samples", "Ticks, bars, labeling", "—", "ml-for-trading repo", "In repo"],
  ["DS33", "Synthetic generators", "All families", "known truth", "sklearn / TradingLab", "Code"],
];

export default function App() {
  const [fam, setFam] = useState<Fam>("R");
  const rows = useMemo((): string[][] => ALGOS[fam].map((r: [string, string, string]) => [r[0], r[1], r[2]]), [fam]);

  return (
    <Page
      title="ARW ML Lab — Architecture & Build Plan"
      summary="Design for a general-purpose tabular Machine Learning Lab in the SP Workstation style: modules, catalogues, financial validation mirrored from ml-for-trading, AI insights and plot-reading decisions from a hosted NVIDIA model, a financial label suitability check, deployment on Vercel, Render and Supabase, and a phase-by-phase Cursor build plan."
      width="wide"
    >
      <TableOfContents
        items={[
          { label: "At a glance" },
          { label: "End-to-end flow" },
          { label: "System architecture" },
          { label: "What came from each repo" },
          { label: "Module map" },
          { label: "AI Dataset Intake / Auto-Setup" },
          { label: "Tech stack" },
          { label: "Algorithm catalogue" },
          { label: "Plots, metrics, CV and tuning" },
          { label: "Financial validation (TradingLab)" },
          { label: "Walk-forward optimisation" },
          { label: "Forecast horizon guard" },
          { label: "Deep learning" },
          { label: "Time series in depth" },
          { label: "Metrics, tables and plots by family" },
          { label: "Classification evaluation suite" },
          { label: "Regression evaluation suite" },
          { label: "Library audit and matrix" },
          { label: "Financial label suitability" },
          { label: "AI Insights layer" },
          { label: "VLM decision agent" },
          { label: "Hosted AI provider (NVIDIA)" },
          { label: "Prediction and uncertainty" },
          { label: "Prediction Studio" },
          { label: "Sample datasets" },
          { label: "Deployment" },
          { label: "Stress test and hardening" },
          { label: "Project kit" },
          { label: "Roadmap" },
          { label: "Deliverables and open items" },
        ]}
      />

      <Section heading="At a glance">
        <Metrics
          metrics={[
            { value: "259", label: "Algorithms", detail: "R62 · C45 · S11 · D28 · K23 · A23 · F67" },
            { value: "244", label: "Plot types", detail: "Estimate, incl. 24 walk-forward plots" },
            { value: "29", label: "CV schemes", detail: "Incl. purged, embargo, CPCV, multilabel stratified" },
            { value: "33", label: "Sample datasets", detail: "19 downloaded locally" },
            { value: "13", label: "Workstation modules" },
            { value: "34", label: "Deep learning and sequence models", detail: "T1–T16 tabular · Q1–Q18 sequential (Q14–Q18 aeon)" },
            { value: "12", label: "AI decision points", detail: "VD1–VD12, human-approved" },
            { value: "20", label: "Diagrams", detail: "PNG + Mermaid source" },
            { value: "150", label: "Pinned libraries", detail: "Library Matrix §44, Python 3.12" },
            { value: "18", label: "Build phases", detail: "0–8 incl. 1A, 2A, 3A, 4A, 5A, 5B, 6A, 6B, 8.1/8.2" },
            { value: "35", label: "Prediction samples", detail: "All 33 datasets, target removed, seed 42" },
          ]}
        />
      </Section>

      <Section heading="End-to-end flow">
        <Diagram
          direction="vertical"
          nodes={[
            { id: "up", label: "Upload or sample", detail: "CSV / Excel / Parquet", kind: "terminal" },
            { id: "prof", label: "AI Dataset Intake", detail: "index, frequency, roles, family with confidence; user confirms" },
            { id: "fam", label: "Choose family", kind: "decision" },
            { id: "sup", label: "Supervised", detail: "auto regression vs classification; sequential or not" },
            { id: "uns", label: "Unsupervised", detail: "DR, clustering, anomaly" },
            { id: "ts", label: "Time series", detail: "analysis + HorizonGuard" },
            { id: "eda", label: "EDA tables + plots", detail: "AI Insights: data issues" },
            { id: "pre", label: "Leakage-safe preprocessing recipe" },
            { id: "lab", label: "Model lab", detail: "defaults or customise every hyperparameter" },
            { id: "cv", label: "CV + tuning jobs", detail: "Celery, Optuna, purged / CPCV / walk-forward" },
            { id: "lb", label: "Leaderboard + statistics", detail: "AI Insights per model" },
            { id: "xp", label: "Explain", detail: "SHAP, LIME, PDP, ICE, ALE" },
            { id: "reg", label: "Registry @champion" },
            { id: "pred", label: "Predict with uncertainty", detail: "probabilities, intervals, confidence", kind: "terminal" },
          ]}
          edges={[
            { from: "up", to: "prof" }, { from: "prof", to: "eda" }, { from: "eda", to: "fam" },
            { from: "fam", to: "sup" }, { from: "fam", to: "uns" }, { from: "fam", to: "ts" },
            { from: "sup", to: "pre" }, { from: "uns", to: "pre" }, { from: "ts", to: "pre" },
            { from: "pre", to: "lab" }, { from: "lab", to: "cv" }, { from: "cv", to: "lb" },
            { from: "lb", to: "xp" }, { from: "xp", to: "reg" }, { from: "reg", to: "pred" },
          ]}
        />
      </Section>

      <Section heading="System architecture">
        <Diagram
          direction="horizontal"
          nodes={[
            { id: "b", label: "Browser", detail: "Next.js 16 SP shell, Plotly, KaTeX", kind: "person" },
            { id: "bff", label: "Vercel: Next.js BFF", detail: "Supabase Auth session, signed uploads; no heavy compute" },
            { id: "core", label: "Render: lab-api", detail: "FastAPI, REST + SSE" },
            { id: "redis", label: "Render Key Value", detail: "Celery broker, noeviction" },
            { id: "w", label: "Render workers", detail: "light (EDA, insights) · train (ML, tuning)" },
            { id: "eng", label: "labcore + TradingLab", detail: "sklearn, GBMs, torch, Nixtla" },
            { id: "st", label: "Supabase", detail: "Postgres + RLS, Auth, Storage" },
            { id: "vlm", label: "NVIDIA API catalog", detail: "hosted VLM + LLM, key on Render only" },
          ]}
          edges={[
            { from: "b", to: "bff", label: "HTTPS" }, { from: "bff", to: "core", label: "JWT" },
            { from: "b", to: "st", label: "direct resumable upload", dashed: true },
            { from: "b", to: "core", label: "SSE progress, direct", dashed: true },
            { from: "core", to: "redis" }, { from: "redis", to: "w" }, { from: "w", to: "eng" },
            { from: "eng", to: "st" }, { from: "w", to: "vlm", label: "q.insights, HTTPS" }, { from: "core", to: "st" },
          ]}
        />
      </Section>

      <Section heading="What came from each repo">
        <Table
          columns={["Repo", "Role", "Taken into the design"]}
          rows={[
            ["sp-workstation", "Look and shell", "Next.js 16 + React 19 + Tailwind 4; gold tokens `#c9a227`; Cormorant / DM Sans / IBM Plex Mono; 280 px collapsible sidebar with Home Terminal and nested module tree; `modules.ts` registry; Home · Analytics · Workbench · Intel · Upload rhythm; OTP + jose JWT"],
            ["blackcarbon-saas", "ML UX, stack split, code layout", "Web → gateway → FastAPI ML service; `backend/ml/{data, preprocess, eda, pipeline, train, explain, predict, registry}`; KaTeX `ExplainCard`; fast / balanced / thorough presets in `param_grids.py`; model × scaler grid; metrics table and diagnostic plots"],
            ["ml-for-trading (TradingLab)", "Financial and sequential toolkit", "PurgedKFold, PurgedSplit, ml_cross_val_score, CombinatorialPurgedKFold; triple barrier and meta-labels; uniqueness, sequential bootstrap, sample weights; FFD; CUSUM filter; volatility, microstructure, structural breaks; MDI / MDA / SFI, ONC; PSR / DSR, Campbell haircut; bet sizing; portfolio optimisation (Phase 7)"],
          ]}
        />
      </Section>

      <Section heading="Module map">
        <Table
          columns={["#", "Module", "Sub-pages"]}
          rows={[
            ["0", "Home Terminal", "Recent experiments, job tape, champions, sample launcher"],
            ["1", "Data", "Upload · Intake Review · Sample Datasets · Explorer · Schema & Types · Versions & Drift · Joins"],
            ["2", "EDA", "Overview · Univariate · Bivariate · Multivariate · Missingness · Outliers · Target · Dependence · Temporal · Quality · Report"],
            ["3", "Preprocess", "Recipe Builder · Imputation · Encoding · Scaling · Outliers · Features · Selection · Imbalance · Financial Features · Leakage Check"],
            ["4", "Supervised", "Task Setup · Model Lab · CV & Tuning · Runs · Leaderboard · Model Detail · Compare · Ensembles · Walk-Forward · Financial Backtest"],
            ["5", "Unsupervised", "Setup · Dim. Reduction · Clustering · Anomaly · Model Selection · Profiles"],
            ["6", "Time Series", "Setup · Analysis · Model Lab · Backtesting · Leaderboard · Forecast · Residuals · Multivariate"],
            ["7", "Explain", "Global · Local · Interactions · Financial FI · Compare"],
            ["8", "Predict", "Single · Batch · What-if · Forecast · Monitoring · API"],
            ["9", "Experiments", "Runs · Compare · Registry · Lineage · Artefacts"],
            ["10", "Reports", "Builder · Templates · History"],
            ["11", "Learn (Logic Atlas)", "Algorithms · Metrics · Plots · Tests · Encodings · CV · Glossary"],
            ["12", "Admin", "Users & Roles · Quotas · Queues · AI providers & budgets · Decision modes · Audit"],
          ]}
        />
        <Text>Every module also carries the AI Insights side panel, and every panel has an info card with its LaTeX math.</Text>
      </Section>

      <Section heading="AI Dataset Intake / Auto-Setup" caption="ARCHITECTURE §33. Runs on every upload and every new version; the user always confirms.">
        <Diagram
          direction="vertical"
          nodes={[
            { id: "u", label: "Upload or new version", detail: "append, replace, upsert", kind: "terminal" },
            { id: "p", label: "Extended column profile" },
            { id: "det", label: "Detectors D1 to D6", detail: "index, frequency, roles, family, targets, leakage" },
            { id: "llm", label: "LLM adjudicator", detail: "profile JSON only, JSON schema" },
            { id: "val", label: "Validator", detail: "hard rules win", kind: "decision" },
            { id: "rev", label: "Intake Review screen", detail: "editable roles, family cards, target choice" },
            { id: "ok", label: "Confirmed task spec", kind: "terminal" },
            { id: "diff", label: "Schema diff + drift", detail: "D7, D8 against parent version", kind: "decision" },
          ]}
          edges={[
            { from: "u", to: "p" }, { from: "p", to: "det" }, { from: "det", to: "llm" }, { from: "llm", to: "val" },
            { from: "val", to: "rev", label: "pass, or rules only on fail" },
            { from: "rev", to: "ok" }, { from: "p", to: "diff" }, { from: "diff", to: "ok", label: "compatible: carry forward" },
            { from: "diff", to: "rev", label: "breaking: re-confirm", dashed: true },
          ]}
        />
        <Table
          columns={["Detector", "What it decides", "Key rules"]}
          rows={[
            ["D1 Index / datetime", "Time index, entity column, row id", "Parse rate 95%, epoch and Excel serial ranges, composite year + quarter, dd/mm vs mm/dd by values over 12, time score 0.6 to accept, panel when (entity, time) is unique"],
            ["D2 Frequency", "Alias, regularity, calendar, seasonal periods", "`infer_freq` then mode of gaps; trading days checked against XNSE / XNYS holidays; intraday sessions; irregular data gets a resample suggestion"],
            ["D3 Column roles", "Feature, OHLCV, volume, return, exog, weight, group, text, PII, constant, duplicate", "OHLCV consistency in 99% of rows; PII regex for email, phone, PAN, Aadhaar; hard excludes can never become features"],
            ["D4 Family + task", "Time series, sequential, non-sequential, unsupervised, with confidence", "Weighted evidence logits, softmax; pre-select at 0.55 or more, else ask; financial flag switches to purged CV and walk-forward"],
            ["D5 Targets + features", "Ranked targets, feature set with encoders", "Name vocabulary, last column, predictability; raw prices never a target, derived triple-barrier or forward-return targets instead"],
            ["D6 Leakage suspects", "Columns held out pending user decision", "Single-feature AUC 0.99, target identities (R² 0.999), post-outcome names, later dates, lead-lag, group and join leakage"],
            ["D7 + D8 Updates", "Compatible or breaking new version", "Add / remove / rename (Jaro-Winkler 0.85), type change, new levels, time overlap; PSI over 0.25 red"],
          ]}
        />
        <Table
          columns={["Sample", "Expected proposal"]}
          rows={[
            ["Titanic", "Non-sequential supervised; target `Survived`; `PassengerId` row id; `Name` excluded; `Cabin` 77% missing"],
            ["Airline Passengers", "Time series; `Month` monthly; m = 12; cap 24"],
            ["US Macrodata", "Time series; composite `year` + `quarter` index"],
            ["NIFTY 50", "Financial sequential; XNSE trading days; OHLCV roles; triple-barrier target proposed instead of `Close`"],
            ["Mall Customers", "Unsupervised; `CustomerID` row id"],
          ]}
        />
      </Section>

      <Section heading="Tech stack">
        <Properties
          items={[
            { label: "Frontend", value: "Next.js 16, React 19, TypeScript, Tailwind 4, Radix, TanStack Query / Table, react-hook-form + zod, Plotly.js, lightweight-charts, KaTeX" },
            { label: "Backend", value: "FastAPI (Python 3.12) on Render, Celery 5 on Render workers + Render Key Value, Supabase Postgres 17 + Auth + Storage, optional MLflow 3, Polars + DuckDB" },
            { label: "Supervised", value: "scikit-learn 1.9.1, XGBoost, LightGBM, CatBoost, NGBoost, quantile-forest, glum, imodels, pytorch-tabular, imbalanced-learn, category_encoders, feature-engine, skrub (TabPFN off: weights licence)" },
            { label: "Evaluation", value: "sklearn.metrics, imbalanced-learn, netcal, MLstatkit (DeLong), mlxtend (5×2cv), statsmodels, scikit-posthocs, fairlearn, cleanlab" },
            { label: "Time series", value: "statsmodels, statsforecast, neuralforecast, mlforecast, hierarchicalforecast, arch, Prophet, pmdarima, sktime, skforecast, darts, aeon, tsfresh" },
            { label: "Unsupervised", value: "umap-learn, hdbscan, openTSNE, pacmap, trimap, pyod + pythresh, tslearn, prince, minisom" },
            { label: "Tuning, XAI, uncertainty", value: "Optuna 5; shap, lime, PyALE, dice-ml, interpret, captum; MAPIE, crepes, venn-abers, NGBoost, calibration" },
            { label: "Financial", value: "vendored TradingLab (ml-for-trading) + new `labcore/finance/pbo.py`" },
            { label: "AI Insights + decisions", value: "Hosted NVIDIA API catalog (OpenAI-compatible): Nemotron 3.5 Super VL primary, Gemma 4 31B and Llama 3.2 90B Vision fallbacks, Nemotron 3 Super for text; numbers-only offline mode" },
            { label: "Ops", value: "GitHub monorepo, GitHub Actions, Vercel + Render Blueprint + Supabase CLI migrations; Docker Compose for local dev; Kubernetes + KEDA only as optional scale-out; Sentry" },
          ]}
        />
      </Section>

      <Section heading="Algorithm catalogue" caption="Every algorithm has a Use defaults / Customise toggle and Quick, Balanced, Thorough and Exhaustive search presets. Every entry is backed by the library shown (ARCHITECTURE §43, §44); entries marked optional are off by default.">
        <Segmented<Fam> options={FAM_OPTS} value={fam} onChange={(v: Fam) => setFam(v)} />
        <Table columns={["ID", "Algorithm", "Library"]} rows={rows} />
      </Section>

      <Section heading="Plots, metrics, CV and tuning">
        <Table
          columns={["Catalogue", "Count", "Examples"]}
          rows={[
            ["EDA plots", "64", "Histogram + KDE, raincloud, Q-Q, missingness matrix, correlation clustermap, pairplot, ACF / PACF, STL, candlestick"],
            ["Supervised plots", "51", "Pred vs actual, residual Q-Q, ROC / PR, calibration, lift, learning and validation curves, CD diagram, equity curve, PBO histogram"],
            ["Explainability outputs", "33", "SHAP beeswarm / waterfall / dependence, LIME, PDP 2D, ICE, ALE, permutation, counterfactuals"],
            ["Unsupervised plots", "53", "Scree, biplot, UMAP / t-SNE grids, elbow, silhouette knife, dendrogram, OPTICS reachability, anomaly scores"],
            ["Time-series plots", "18", "Forecast fan, error by horizon, residual ACF, VaR breaches, impulse response"],
            ["Classification metrics", "55", "MCC, κ / QWK, Youden J, G-mean, log loss, Brier + decomposition, ROC-AUC OvR / OvO, PR-AUC, KS, Gini, ECE, expected cost (§41)"],
            ["Regression metrics", "40", "RMSE, MAE, MAPE / sMAPE, R² / adjusted R², pinball, CRPS, interval score, Huber, D² scores (§42)"],
            ["CV schemes", "29", "KFold, stratified, group, nested, walk-forward, purged K-fold, CPCV, predefined, multilabel stratified, .632+ bootstrap"],
            ["Tuning methods", "10", "Grid, random, halving, TPE (default), CMA-ES, GP, Hyperband / ASHA, NSGA-II"],
            ["Encoders", "32", "One-hot, target (K-fold), WOE, CatBoost, James-Stein, hashing, binary, embeddings, MinHash, Gap, decision-tree, rare-label"],
          ]}
        />
      </Section>

      <Section heading="Financial validation (TradingLab)">
        <Table
          columns={["Step", "TradingLab file → function", "Lab rule"]}
          rows={[
            ["Events", "`filters/event_filters.py` → `cusum_filter`", "Sample on CUSUM events"],
            ["Labels", "`labeling/triple_barrier_labeling.py` → `add_vertical_barrier`, `get_events`, `get_bins`", "Meta-labels when a side model exists"],
            ["Uniqueness", "`sampling/concurrent.py`, `sampling/bootstrapping.py` → `seq_bootstrap`", "Weights computed once on the timeline"],
            ["Weights", "`sample_weights/attribution.py` → by return, by time decay", "Sliced per fold into train and score weights"],
            ["Stationarity", "`features/fractional_differentiation.py` → `frac_diff_ffd`", "d* chosen on train rows only"],
            ["Purged CV", "`cross_validation/time_series_cv.py` → `PurgedKFold`, `ml_cross_val_score`", "Default k=5, embargo 1%"],
            ["CPCV", "`cross_validation/combinatorial.py` → `CombinatorialPurgedKFold`", "N=6, k=2 → 15 splits, 5 paths"],
            ["PBO", "Not in TradingLab → new `labcore/finance/pbo.py` (CSCV, S=16)", "Champion only if PBO < 0.2"],
            ["Sharpe tests", "`backtest_statistics/strategy_metrics.py` → PSR, DSR; `campbell.py`", "DSR > 0.95 with trials = Optuna trials"],
            ["Feature importance", "`feature_importance/importance.py` → MDI, MDA, SFI; `clustering/onc.py`", "Clustered importance across purged folds"],
          ]}
        />
      </Section>

      <Section heading="Walk-forward optimisation" caption="ARCHITECTURE §32. TradingLab has no walk-forward driver, so the lab builds it on TradingLab primitives.">
        <Properties
          items={[
            { label: "Modes", value: "Rolling, anchored, anchored with time decay, calendar-aligned, CUSUM event-based" },
            { label: "Daily defaults", value: "In-sample 504 bars, out-of-sample 63, step 63, gap = label horizon, purge on, embargo 1%" },
            { label: "Per window", value: "Recipe and FFD d* fit on in-sample only; Optuna re-tune with inner purged K-fold, warm start, plateau selection; every trial stored" },
            { label: "Schedules", value: "fixed, every window, every k, calendar, performance trigger, drift trigger, frozen; frozen and fixed always run as baselines" },
            { label: "Costs", value: "Commission, slippage, half-spread, STT, square-root impact, borrow; sensitivity sweep and break-even multiple" },
            { label: "Robustness", value: "Block bootstrap, signal permutation, trade shuffle, Hansen SPA, parameter jitter" },
          ]}
        />
        <Diagram
          direction="horizontal"
          nodes={[
            { id: "plan", label: "Window planner", detail: "purge + embargo" },
            { id: "tune", label: "Per-window re-tune", detail: "inner purged CV" },
            { id: "fit", label: "Retrain by policy" },
            { id: "oos", label: "Predict OOS + costs" },
            { id: "st", label: "Stitched OOS curve" },
            { id: "ver", label: "Verdict", detail: "DSR, PBO, WFE, MC", kind: "decision" },
          ]}
          edges={[
            { from: "plan", to: "tune" }, { from: "tune", to: "fit" }, { from: "fit", to: "oos" },
            { from: "oos", to: "st", label: "after last window" }, { from: "st", to: "ver" },
          ]}
        />
        <Table
          columns={["Check", "Definition", "Champion rule"]}
          rows={[
            ["Walk-forward efficiency", "Annualised OOS return / annualised IS return; also Sharpe ratio version", "0.5 or more"],
            ["Profitable windows", "Share of windows with net OOS return above 0, binomial test", "60% or more"],
            ["Deflated Sharpe", "Stitched net Sharpe, trials N = every configuration tried in every window", "Above 0.95"],
            ["PBO", "CSCV on top-10 candidates re-scored in every window", "Below 0.2"],
            ["Monte Carlo", "Signal-permutation p-value; bootstrap CI for Sharpe and drawdown", "p below 0.05"],
            ["Parameter stability", "Normalised distance between windows, Kendall τ, CV per parameter", "Reported, drives insights"],
            ["CPCV cross-check", "Percentile of walk-forward Sharpe among CPCV paths", "Top 10% with high PBO flags a lucky path"],
          ]}
        />
        <Table
          columns={["Walk-forward step", "TradingLab file → function"]}
          rows={[
            ["Purge at window boundary", "`cross_validation/time_series_cv.py` → `ml_get_train_times`"],
            ["Inner tuning CV", "`PurgedKFold`, `ml_cross_val_score` with train and score weights"],
            ["CPCV cross-check", "`cross_validation/combinatorial.py` → `CombinatorialPurgedKFold`"],
            ["Labels and events", "`cusum_filter`, `get_daily_vol`, `add_vertical_barrier`, `get_events`, `get_bins`"],
            ["Weights", "`get_av_uniqueness_from_triple_barrier`, `get_weights_by_return`, `get_weights_by_time_decay`"],
            ["Per-window stationarity", "`frac_diff_ffd`, `plot_min_ffd`"],
            ["Position sizing", "`bet_size_probability`, `bet_size_dynamic`, `bet_size_budget`, `bet_size_reserve`, `M2N`"],
            ["Statistics", "`strategy_metrics.py` Sharpe, PSR, DSR, MinTRL, drawdowns; `CampbellBacktesting` haircut"],
            ["Regimes", "`structural_breaks/sadf.py` → `get_sadf`"],
          ]}
        />
        <Table
          columns={["Outputs", "Contents"]}
          rows={[
            ["24 plots", "Window timeline, stitched equity, underwater, IS vs OOS bars with WFE, parameter stability heatmap, parameter drift lines, objective surfaces, Monte Carlo fan and histograms, cost decomposition, feature-importance drift, regimes, policy comparison, CPCV vs walk-forward"],
            ["2 tables", "Per-window table (dates, purged counts, params, IS vs OOS, costs, WFE) and summary table with verdict"],
            ["API", "`/wfo/plan`, `/wfo/runs`, windows, stitched, params, montecarlo, costs re-pricing, pbo, cpcv-compare, events, compare, promote"],
            ["Database", "`wfo_runs`, `wfo_windows`, `wfo_trials`, `wfo_series`, `wfo_mc_results`"],
            ["AI Insights", "Stage `wfo`: is the edge real, robustness over time, unstable parameters, cost sensitivity, value of retraining"],
          ]}
        />
      </Section>

      <Section heading="Forecast horizon guard">
        <Table
          columns={["Frequency", "Recommended h", "Hard max h"]}
          rows={[
            ["Hourly", "24", "168"],
            ["Daily", "14", "90"],
            ["Trading days", "5", "21 (66 for volatility)"],
            ["Weekly", "13", "52"],
            ["Monthly", "12", "36"],
            ["Quarterly", "8", "16"],
            ["Yearly", "3", "10"],
          ]}
        />
        <Text>The final cap is the minimum of the frequency cap, data feasibility (n/3, backtest windows, SARIMA needs p+q+P+Q+d+mD+1 points, seasonal ETS needs 2m) and model caps. After backtesting, steps past the last one that beats seasonal naive on MASE are drawn dashed. Airline passengers (144 months) gets a cap of 24.</Text>
      </Section>

      <Section heading="AI Insights layer">
        <Table
          columns={["Model ID (NVIDIA API catalog)", "Inputs", "Licence / terms", "Role"]}
          rows={[
            ["`nvidia/nemotron-3.5-super-vl-120b-a12b`", "text, image, video", "OpenMDW-1.1, commercial use allowed", { text: "Primary VLM", tone: "success" }],
            ["`google/gemma-4-31b-it`", "text, image", "NVIDIA Open Model + Apache-2.0", "Fallback VLM 1"],
            ["`meta/llama-3.2-90b-vision-instruct`", "text, image", "Llama Community", "Fallback VLM 2"],
            ["`nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`", "text, image, video", "NVIDIA open model", "Fast tier (per-artefact)"],
            ["`nvidia/nemotron-3-super-120b-a12b`", "text", "NVIDIA open model", { text: "Primary text LLM", tone: "success" }],
            ["`deepseek-ai/deepseek-v4.1-flash` · `openai/gpt-oss-20b`", "text", "per card", "Text fallbacks"],
            ["`nvidia/nemotron-3-ultra-550b-a55b`", "text", "NVIDIA open model", "Deep mode narratives"],
          ]}
        />
        <Sequence
          actors={[
            { id: "ui", label: "Insights panel" },
            { id: "api", label: "lab-core" },
            { id: "cb", label: "Context builder" },
            { id: "vlm", label: "NVIDIA-hosted VLM" },
            { id: "val", label: "Validator" },
          ]}
          messages={[
            { from: "ui", to: "api", label: "request stage + artefact IDs" },
            { note: "Cache hit on input hash + model + prompt version returns at once", over: "api" },
            { from: "api", to: "cb", label: "PNGs, numbers, tables, rule findings" },
            { from: "cb", to: "vlm", label: "FACTS with fact IDs + images, JSON schema" },
            { from: "vlm", to: "ui", label: "token stream (SSE)", reply: true },
            { from: "vlm", to: "val", label: "draft JSON" },
            { note: "Every number must match FACTS; every claim cites an ID; one repair round", over: "val" },
            { from: "val", to: "ui", label: "validated insight", reply: true },
          ]}
        />
        <Callout tone="info">All model IDs were checked against the live `integrate.api.nvidia.com/v1/models` list on 14 Nov 2026. Gemini, OpenRouter and Groq are optional fallback providers, off by default. If no provider is reachable the panel falls back to numbers-only insights.</Callout>
      </Section>

      <Section heading="VLM decision agent" caption="ARCHITECTURE §38. The model looks at the rendered plots and proposes a choice; rule guards and the user decide.">
        <Diagram
          direction="horizontal"
          nodes={[
            { id: "o", label: "Observe", detail: "render plots + FACTS" },
            { id: "b", label: "Rule baseline" },
            { id: "p", label: "VLM proposal", detail: "JSON schema, cites facts" },
            { id: "g", label: "Hard guards", kind: "decision" },
            { id: "r", label: "Decision card", detail: "approve / edit / reject", kind: "person" },
            { id: "a", label: "Apply new config version" },
            { id: "l", label: "Audit log + reflection", kind: "terminal" },
          ]}
          edges={[
            { from: "o", to: "b" }, { from: "b", to: "p" }, { from: "p", to: "g" },
            { from: "g", to: "r", label: "pass or blocked" }, { from: "r", to: "a" }, { from: "a", to: "l" },
          ]}
        />
        <Table
          columns={["ID", "Decision", "Plots the VLM sees", "Hard guard"]}
          rows={[
            ["VD1", "Task family and column roles", "missingness, index line, target distribution", "leakage rules; user-locked roles stay"],
            ["VD2", "Preprocessing recipe", "histograms, box plots, missingness, correlation, VIF", "no target-aware step outside CV"],
            ["VD3", "Model families and preset", "baseline learning curve, PCA 2D", "licence and GPU flags, time budget"],
            ["VD4", "CV scheme", "index timeline, target ACF", "no shuffled CV on sequential data; purged for financial"],
            ["VD5", "Forecast horizon and season", "line, ACF/PACF, periodogram, STL", "h never above HorizonGuard h_max"],
            ["VD6", "Differencing / Box-Cox", "ACF before/after, rolling std", "d + D ≤ 2"],
            ["VD7", "Number of components", "scree, cumulative variance, parallel analysis", "Bartlett must be significant"],
            ["VD8", "Number of clusters and algorithm", "elbow, silhouette, gap, UMAP coloured by k", "stability ≥ 0.6, no cluster under 2%"],
            ["VD9", "Financial label method and parameters", "barrier grid, label balance, volatility", "only methods the suitability check allows"],
            ["VD10", "Champion model", "leaderboard, CD diagram, calibration", "DSR > 0.95 and PBO < 0.2 for financial"],
            ["VD11", "Calibration and threshold", "reliability, threshold sweep, cost curve", "calibrator fit on held-out folds"],
            ["VD12", "Retrain / drift action", "PSI bars, score drift", "never auto-retrain without approval"],
          ]}
        />
      </Section>

      <Section heading="Hosted AI provider (NVIDIA)" caption="ARCHITECTURE §40. No self-hosted model and no GPU host needed for AI.">
        <Properties
          items={[
            { label: "Endpoint", value: "`https://integrate.api.nvidia.com/v1` (OpenAI-compatible chat completions with `image_url` data URIs)" },
            { label: "Key", value: "`NVIDIA_API_KEY` as a Render secret on lab-api and workers only; never in Vercel or the browser" },
            { label: "Free tier", value: "Trial for development and testing; per-model limits not published (about 40 requests a minute observed). Production needs an NVIDIA AI Enterprise licence or a paid endpoint" },
            { label: "Images", value: "1024×640 plots, palette PNG or JPEG, base64 kept under 170 KB (NVIDIA inline limit 180 KB), big grids tiled" },
            { label: "Retries", value: "Back-off with jitter, up to 4 attempts, honour Retry-After; 404/403 moves to the next model; circuit breaker after 3 failures" },
            { label: "Cost controls", value: "Cache by content hash, lazy generation, fast model for per-plot calls, daily caps per workspace (500) and per user (150)" },
            { label: "Data sent", value: "Aggregate plots and FACTS only, never raw rows; PII redacted; restricted workspaces stay numbers-only" },
            { label: "Fallbacks", value: "Gemini API, OpenRouter, Groq or any OpenAI-compatible endpoint (off by default); numbers-only offline mode always works" },
          ]}
        />
      </Section>

      <Section heading="Deep learning" caption="ARCHITECTURE §34. Every hyperparameter has a default and a search space.">
        <Table
          columns={["Group", "Models", "Key defaults"]}
          rows={[
            ["Tabular T1–T16", "MLP, ResNet-MLP, TabNet, FT-Transformer, TabTransformer, SAINT, NODE, AutoInt, DCN-v2, GANDALF, GATE, DANet, TabPFN (off: non-commercial weights), MDN, stacked, self-supervised pre-training", "AdamW lr 1e-3, early stopping patience 10, embedding dim min(50, (cardinality+1)//2), seed 42"],
            ["Sequential Q1–Q13", "RNN, LSTM, GRU, BiLSTM (guarded), attention-LSTM, CNN-1D, TCN, CNN-LSTM, Transformer, patch encoder, TFT, xLSTM / Mamba, sequential-bootstrap bagging", "lookback window, purge and embargo for financial windows"],
            ["Training plots (17)", "loss and metric curves, LR finder, LR trace, gradient norms, weight and activation histograms, attention maps, TabNet masks, embeddings, latent space, trials, fold curves, uncertainty, saliency, architecture", "—"],
            ["Tables (9)", "architecture, hyperparameters, epochs, early stop, folds, trials, uncertainty, resources, attention", "—"],
            ["Uncertainty", "MC dropout (50 passes), deep ensembles (5 seeds 42–46), quantile and NLL heads, conformal, temperature scaling", "—"],
            ["CPU / GPU", "Render CPU workers run Quick/Balanced small models; GPU-only models need an optional external GPU worker and otherwise refuse with a reason", "—"],
          ]}
        />
      </Section>

      <Section heading="Time series in depth" caption="ARCHITECTURE §35.">
        <Table
          columns={["Area", "Contents"]}
          rows={[
            ["EDA", "classical / STL / MSTL / X-13 decomposition, ACF/PACF, lag, seasonal and subseries plots, periodogram, spectrogram, rolling stats, calendar heatmap, breaks, volatility clustering, CCF, Granger heatmap"],
            ["Test tables", "ADF, KPSS, Phillips-Perron, Zivot-Andrews, DF-GLS, OCSB / Canova-Hansen, CUSUM / Bai-Perron, ARCH-LM, normality, Ljung-Box, Granger, CCF, Engle-Granger / Johansen, plus a combined stationarity verdict"],
            ["Models", "F1–F54 with every hyperparameter, default and search space (ETS, ARIMA family, Theta, TBATS, MSTL, Prophet, VAR, GARCH, ML lag models, N-BEATS, N-HiTS, TFT, PatchTST, iTransformer and more)"],
            ["Multi-step", "recursive, direct, DirRec, MIMO, DIRMO, rectify — a leaderboard column"],
            ["Exogenous", "static, past-only (auto-lagged), known-future (coverage checked), generated calendar and Fourier terms"],
            ["Hierarchical", "global models, VAR family, reconciliation BottomUp / TopDown / MiddleOut / MinTrace / ERM"],
            ["Metrics", "ME, MAE, RMSE, MAPE, sMAPE, WAPE, MASE, RMSSE, MSIS, Winkler, coverage, interval width, pinball, CRPS, Theil U1/U2, directional accuracy, QLIKE, Kupiec / Christoffersen"],
            ["Diagnostics + leaderboards", "Ljung-Box, Jarque-Bera, ARCH-LM, Breusch-Godfrey, Durbin-Watson; leaderboards overall, by horizon, by window, by series, Diebold-Mariano, ensembles"],
          ]}
        />
      </Section>

      <Section heading="Metrics, tables and plots by family" caption="ARCHITECTURE §36. Each metric has its formula and how to read it; each table lists exact columns.">
        <Table
          columns={["Family", "Algorithms", "Metrics", "Tables", "Plots"]}
          rows={[
            ["Regression", "62", "40 (§42)", "17", "36"],
            ["Classification", "45", "55 (§41)", "42", "45"],
            ["Deep learning", "16 tabular + 13 sequential", "supervised set + training and uncertainty scores", "9", "17"],
            ["Time series", "67 + 6 strategies + 5 reconciliations", "22", "22", "41 + 7 residual"],
            ["Dimensionality reduction", "28", "20 (incl. KMO, Bartlett, trustworthiness, continuity, stress)", "8", "16 (scree, biplot, correlation circle, loadings heatmap, Shepard, 2D/3D)"],
            ["Clustering", "23", "16 (silhouette, CH, DB, Dunn, gap, BIC, stability, ARI, NMI, V-measure, FMI)", "9", "20 (elbow, silhouette knife, dendrogram, k-distance, reachability, radar, parallel coordinates)"],
            ["Anomaly detection", "23", "7", "5", "9"],
          ]}
        />
      </Section>

      <Section heading="Classification evaluation suite" caption="ARCHITECTURE §41. Runs on every binary, multiclass and multilabel model, on CV out-of-fold predictions, per fold, CV-aggregated and on the test split.">
        <Metrics
          metrics={[
            { value: "55", label: "Metrics", detail: "With formulas and averaging modes" },
            { value: "42", label: "Tables" },
            { value: "45", label: "Plots" },
            { value: "13", label: "Threshold methods" },
            { value: "11", label: "Statistical tests" },
            { value: "8", label: "AI insight templates" },
          ]}
        />
        <Table
          columns={["Confusion matrix", "What it shows", "Library"]}
          rows={[
            ["CLE.T.CM", "Raw counts", "sklearn confusion_matrix"],
            ["CM_NORM_TRUE / PRED / ALL", "Row-normalised (recall view), column-normalised (precision view), all-normalised", "confusion_matrix(normalize=…)"],
            ["CM_FOLDS / CM_CV", "One matrix per fold; pooled sum plus mean ± std of each normalised cell", "sklearn + numpy"],
            ["CM_COST / CM_WEIGHTED", "Cost matrix applied to counts; sample-weighted counts", "numpy on sklearn output"],
            ["CM_MULTILABEL", "2 × 2 per label (multilabel) and one-vs-rest per class", "multilabel_confusion_matrix"],
            ["CM_THRESHOLD / CM_DELTA", "Default 0.5 vs tuned threshold; model A minus model B", "sklearn"],
            ["CM_DERIVED", "TP, FP, TN, FN, specificity, NPV, FPR, FNR, likelihood ratios per class", "sklearn"],
          ]}
        />
        <Table
          columns={["Classification report (CLE.T.REPORT)", "Contents"]}
          rows={[
            ["Per-class columns", "Precision, recall, F1, F-β, support, specificity, NPV, FPR, FNR, one-vs-rest ROC-AUC, AP and Brier"],
            ["Summary rows", "Macro, micro, weighted and (multilabel) samples averages; accuracy; balanced and adjusted balanced accuracy"],
            ["Variants", "CV mean ± std, per fold, train vs CV vs test, imbalanced-learn report (G-mean, IBA)"],
            ["CV metrics table", "Every metric: mean, std, SEM, min, max, 95% CI, pooled out-of-fold, train gap, test value with bootstrap CI"],
          ]}
        />
        <Table
          columns={["Area", "Contents"]}
          rows={[
            ["Plots", "Heatmaps in 4 normalisations, per-class ROC with micro and macro ROC, PR with iso-F1 lines, reliability diagram with histogram, cumulative gain, lift, KS, DET, threshold vs metric, discrimination threshold, cost curves, class-probability distributions, per-class P/R/F1 bars"],
            ["Threshold methods", "Default, Youden, closest to top-left, F-β max, MCC max, minimum cost, precision at recall, recall at precision, FPR budget, capacity, equal error rate, KS, prevalence match"],
            ["Statistical tests", "McNemar, Cochran Q, DeLong (MLstatkit), 5×2cv t and F (mlxtend), corrected resampled t, Wilcoxon, Friedman + Nemenyi, bootstrap, Holm, Hosmer–Lemeshow"],
            ["Error analysis", "Most confident wrong predictions, top confusions, metrics by segment (fairlearn), label issues (cleanlab)"],
          ]}
        />
        <Callout tone="info">Thresholds and calibrators are fitted on training out-of-fold predictions only; the test split is never read. Undefined ratios show a dash, never zero. Under imbalance, accuracy is never the headline metric.</Callout>
      </Section>

      <Section heading="Regression evaluation suite" caption="ARCHITECTURE §42. Audit of the regression evaluation, completed in the same style.">
        <Metrics
          metrics={[
            { value: "40", label: "Metrics" },
            { value: "17", label: "Tables" },
            { value: "36", label: "Plots" },
            { value: "6", label: "AI insight templates" },
          ]}
        />
        <Table
          columns={["Area", "Contents"]}
          rows={[
            ["Metrics", "MAE, MSE, RMSE, RMSLE, MAPE, sMAPE, MedAE, max error, R², adjusted R², explained variance, Poisson / Gamma / Tweedie deviance, D² scores, pinball, CRPS, interval score, coverage, Huber"],
            ["Tables", "Row-level residuals, residual tests with verdicts (Shapiro, Jarque–Bera, Breusch–Pagan, White, Durbin–Watson, Ljung–Box, RESET), influence (leverage, Cook's distance, DFFITS), calibration bins, CV metrics, intervals, baselines, comparison"],
            ["Plots", "Predicted vs actual, residuals vs fitted, scale-location, Q-Q, Cook's distance, studentised residuals, partial residuals, Bland–Altman, REC curve, calibration in bins, interval coverage"],
          ]}
        />
      </Section>

      <Section heading="Library audit and matrix" caption="ARCHITECTURE §43 and §44, docs/GAP_AUDIT.md. Every algorithm, encoder, metric, test and plot comes from a popular, maintained library; lab code is limited to thin wrappers.">
        <Table
          columns={["Catalogue", "Before", "After"]}
          rows={[
            ["Regression algorithms", "51", "62"],
            ["Classification algorithms", "35", "45"],
            ["Sequential models", "13", "18"],
            ["Dimensionality reduction", "22", "28"],
            ["Clustering", "19", "23"],
            ["Anomaly detection", "14", "23"],
            ["Forecasting", "54", "67"],
            ["Encoders", "22", "32"],
            ["CV schemes", "20", "29"],
            ["EDA tables", "19", "26"],
          ]}
        />
        <Table
          columns={["Decision", "Libraries"]}
          rows={[
            ["Pinned for compatibility", "numpy 2.4.6, scipy 1.17.1 (aeon), pandas 2.3.3 and torchmetrics 1.8.2 (pytorch-tabular), ngboost 0.5.11"],
            ["Separate optional images", "ydata-profiling, evidently, AutoGluon, H2O, Chronos, TimesFM, xLSTM / Mamba (GPU)"],
            ["Removed", "pykalman, tsai, pytorch-widedeep, confidenceinterval (replaced by MLstatkit), uni2ts"],
            ["Licence review, not imported", "alibi (BSL-1.1), PHATE, kmedoids, pycatch22, minepy, pingouin (GPL); TabPFN weights"],
            ["Optional, off by default", "ResNet-MLP, SAINT, DCN-v2, autoencoder DR, DEC, K-Medoids, Anchors, hv-block CV, Friedman H"],
          ]}
        />
        <Text>The kit pins 150 libraries in backend/requirements with lock files resolved for Python 3.12. Each catalogue table in the architecture has a Library column, and a Cursor rule blocks imports that are not in the matrix.</Text>
      </Section>

      <Section heading="Financial label suitability" caption="ARCHITECTURE §37. Runs before triple barrier, meta-labelling, fixed horizon or trend scanning.">
        <Table
          columns={["Checks", "Examples (pass threshold)"]}
          rows={[
            ["Data FS1–FS8", "time index, price or returns found, positive prices, OHLC consistent, under 2% missing bars, at least 1,000 bars, volatility estimable, under 5% stale prices"],
            ["Trial labels FS9–FS13", "at least 300 CUSUM events, minority class at least 15%, under 60% ended by the time barrier, average uniqueness at least 0.3, effective sample at least 200"],
            ["Context FS14–FS20", "return autocorrelation, minimum FFD d, SADF bubbles, trend-scan t-values, a primary model for meta-labels, fixed-horizon balance, leakage"],
            ["Outcome", "Suitable / Suitable with cautions / Not suitable per method, a 36-cell barrier grid preview, recommendations, and a fallback to standard targets"],
          ]}
        />
      </Section>

      <Section heading="Prediction and uncertainty">
        <Table
          columns={["Output", "Methods"]}
          rows={[
            ["Class probabilities", "Platt, isotonic, temperature, Venn-Abers calibration; ECE and Brier"],
            ["Prediction sets", "Conformal LAC / APS / RAPS (MAPIE)"],
            ["Regression intervals", "Split / CV+ / jackknife+ conformal, quantile GBM / QRF, NGBoost, bootstrap, MC dropout, Bayesian"],
            ["Forecast intervals", "Model-based, bootstrap, conformal, quantile loss; coverage and Winkler score"],
            ["Confidence score", "0 to 100 from calibrated probability or interval width, OOD distance and ensemble disagreement"],
          ]}
        />
      </Section>

      <Section heading="Prediction Studio" caption="ARCHITECTURE §45, diagram 20. Two ways to predict, both driven by the feature contract saved at training. Built in Phase 3A.">
        <Table
          columns={["", "A. Batch upload", "B. Custom input form"]}
          rows={[
            ["Input", "CSV, XLSX or Parquet (download a template with the exact columns first)", "Form generated from the contract: slider + number box, dropdown of seen categories, toggle, date picker, lookback window editor"],
            ["Checks", "PV01–PV16: file type and size, zip bomb, missing or extra columns, target column dropped, dtypes, unseen categories, ranges, OOD, drift, time order, horizon cap, CSV injection, PII masking", "Same checks per field; out-of-range and OOD flags shown live"],
            ["Runs", "Celery job in 50k-row chunks with progress bar and cancel", "Live single-row prediction, 300 ms after each change"],
            ["Output", "Results grid + CSV / XLSX download + summary plots", "Result card with gauge, local SHAP waterfall, what-if sliders, AI explanation"],
            ["Helpers", "Validation report with fixes; humility rules (warn, abstain, review)", "Fill from a random training row; reset to defaults; add to batch"],
          ]}
        />
        <Table
          columns={["Task", "Columns in the output"]}
          rows={[
            ["Regression", "prediction, lower and upper bound per chosen level (conformal, quantile or NGBoost), interval method"],
            ["Classification", "class, calibrated probability per class, confidence, margin, entropy, threshold used, conformal prediction set"],
            ["Time series", "forecast per step with interval bounds, capped by HorizonGuard"],
            ["Clustering and DR", "cluster, distance or soft membership, outlier flag, embedding coordinates"],
            ["Every task", "OOD score and flag, out-of-range and unseen-category lists, imputed fields, optional SHAP top contributors"],
          ]}
        />
        <Text>Endpoints: GET /models/:id/schema, GET /models/:id/template, POST /predict/single, POST /predict/batch, plus job status, results, download and cancel. Tables model_signatures, prediction_jobs and prediction_results ship in the kit migrations with RLS tests. Every dataset DS1–DS33 has a ready-made prediction file in data/samples/predict (35 files): DS29 rows are schema-derived, DS32 is synthetic (private repo) and DS33 is synthetic by design; the rest come from the real data.</Text>
      </Section>

      <Section heading="Sample datasets" caption="Default seed 42 for every preset. URL checks run 14 Nov 2026 (IST).">
        <Table columns={["ID", "Dataset", "Task", "Target", "Source", "Status"]} rows={DATASETS} />
      </Section>

      <Section heading="Deployment" caption="ARCHITECTURE §39. Primary path; Kubernetes is an optional later scale-out for workers.">
        <Table
          columns={["Platform", "Runs", "Starting plan (Nov 2026)"]}
          rows={[
            ["GitHub", "Private monorepo, Actions CI (lint, types, tests, RLS) and deploy (migrations → Render → smoke test)", "—"],
            ["Vercel", "Next.js frontend only (Root Directory `frontend`); 4.5 MB body limit, so uploads go straight to Supabase", "Pro for company use"],
            ["Render web", "`lab-api` FastAPI", "1c-2g, then 2c-4g"],
            ["Render workers", "`lab-worker-light` (EDA, insights, reports, batch prediction) and `lab-worker-train` (ML, tuning, explain, forecast, heavy prediction)", "2c-4g and 4c-16g (8c-32g for Thorough)"],
            ["Render cron job", "`lab-beat`: hourly retention cleanup and stale-job reaper", "0.5c-512mb"],
            ["Render Key Value", "Celery broker, noeviction, internal only", "1g"],
            ["Supabase", "Postgres 17 with RLS, Auth email OTP, Storage buckets, CLI migrations", "Pro, with the global file size limit raised (Free caps uploads at 50 MB)"],
            ["NVIDIA API catalog", "Hosted VLM and LLM, called from Render", "Free trial key; licence for production"],
          ]}
        />
      </Section>

      <Section heading="Stress test and hardening" caption="ARCHITECTURE §46 and docs/STRESS_TEST.md. Round-4 red-team audit of the whole kit, 15 Nov 2026.">
        <Table
          columns={["Severity", "Findings", "Examples"]}
          rows={[
            ["Critical", "3", "Users could write metrics, audit and AI-usage rows; users could change job status; services could deploy before migrations"],
            ["High", "13", "Storage path cast errors, no bucket limits, Supabase Free 50 MB cap, PII in feature contracts, SSE through Vercel, CSV injection, zip bombs, pickle loading, unpinned libraries"],
            ["Medium", "25", "RLS performance, retention, API and env mismatches, Windows CSV MIME type, leakage guarantees, backups of Storage, no resume protocol for Cursor"],
            ["Low", "9", "Drifted embedded config, undocumented CI variable, CLI version pin"],
          ]}
        />
        <Text>Fixed in the kit: a hardening migration (worker-only writes, cancel RPC, heartbeats, idempotency keys, bucket limits, faster RLS), deploy ordering, 15 newly pinned libraries, aligned configs and docs, and a Docker-free database test harness: 6 of 6 migrations applied and 14 of 14 RLS assertions passed. The rest is specified with acceptance criteria for the phase that builds it. The comparison with PyCaret, AutoGluon, H2O, DataRobot, Dataiku, Vertex AI, MLJAR, Orange, KNIME and Weka added humility rules, refit on full data, leaderboard and notebook exports and prediction logs.</Text>
      </Section>

      <Section heading="Project kit" caption="Ready to copy into C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab. Private repo code is not included.">
        <Table
          columns={["Path", "Contents"]}
          rows={[
            ["`CURSOR_KICKOFF.md`", "Short message to paste into a new Cursor Agent chat, plus a one-line continue message"],
            ["`CURSOR_PROMPT.md`, `AGENTS.md`, `README.md`", "Phase-by-phase Cursor prompt with an execution protocol (definition of done, no stubs, self-check, resume), agent instructions, overview"],
            ["`.cursor/rules/*.mdc`", "11 rules: core, stack, Python, frontend, ML integrity (incl. evaluation integrity), AI provider, testing, phase order, deployment, security, use established libraries"],
            ["`docs/`", "ARCHITECTURE v2.2 (§1–§46), FLOWCHART, 20 diagrams (PNG + Mermaid), GAP_AUDIT, STRESS_TEST, feature-contract schema, PROGRESS tracker"],
            ["`backend/requirements/`", "Pinned requirements per Render service, optional images and uv lock files (Python 3.12)"],
            ["`data/samples/`", "19 sample datasets, URLs, manifest (JSON + CSV), 33 presets with seed 42, and 35 prediction samples with feature contracts"],
            ["`scripts/`, `tests/`", "Prediction-sample generator; sample tests and a Docker-free migration and RLS test runner"],
            ["`render.yaml`, `frontend/vercel.json`, `supabase/`, `.github/workflows/`", "Render Blueprint (incl. lab-beat cron), Vercel config, 6 migrations with RLS, storage buckets, Prediction Studio tables and hardening, 2 RLS test files, CI and deploy workflows"],
            ["`.env.example`, `.gitignore`", "Variables per platform; `refs/` and secrets ignored"],
            ["`frontend/ backend/ labcore/ infra/ vendor/`", "Skeleton folders (only backend/requirements is filled)"],
          ]}
        />
      </Section>

      <Section heading="Roadmap">
        <Table
          columns={["Phase", "Scope", "Exit test"]}
          rows={[
            ["0 Foundations", "Monorepo, local Supabase, SP shell, Supabase Auth, migrations + RLS, queues, SSE", "13 modules render; RLS tests pass"],
            ["8.1 Hosted skeleton", "GitHub repo, Render Blueprint, Supabase project, Vercel, CI/CD", "Sample EDA job runs on the hosted stack"],
            ["1 Data + EDA", "Upload, type inference, task wizard, all EDA, education, rule insights", "All EDA artefacts on Titanic, Airline, NIFTY"],
            ["1A AI Dataset Intake", "Detectors D1 to D8, Intake Review screen, versioning, schema diff and drift", "Golden intake results on 8 samples + synthetic leaks"],
            ["2 Supervised core", "Recipes, 32 encoders, R / C registries, CV, tuning, leaderboard, classification and regression evaluation suites", "Leakage tests and golden bands pass; confusion matrix in 3 normalisations and full classification report render"],
            ["2A Deep learning", "Training engine, T1–T16, Q1–Q13, DL plots and tables, uncertainty", "CPU Quick runs under 10 min; GPU-only models refuse cleanly"],
            ["3 Explain + Predict", "SHAP and friends, calibration, conformal, feature contracts, registry, ONNX, notebook export", "Coverage within 2 points; SHAP additivity"],
            ["3A Prediction Studio", "Batch upload with validation and downloads; custom input form; what-if; humility rules; samples for all 33 datasets", "Sample files score with zero blocking issues; single and batch outputs match"],
            ["4 Time series", "Analysis, 67 forecasters, backtests, HorizonGuard", "Airline cap 24; SARIMA beats seasonal naive"],
            ["4A Time series full", "TS EDA and tests, all hyperparameters, multi-step, exogenous, hierarchy, metrics, diagnostics", "Metric unit tests; MinTrace coherence"],
            ["5B Label suitability", "FS1–FS20, grid preview, fallback", "NIFTY suitable; airline falls back"],
            ["5 Financial", "TradingLab adapters, purged CV, CPCV, PBO, DSR, sequential DL", "TradingLab contract tests pass"],
            ["5A Walk-forward", "Planner, per-window re-tuning, retrain policies, stitching, costs, Monte Carlo, verdict", "Purge parity with `ml_get_train_times`; edge vs noise tests"],
            ["6 Unsupervised + AI Insights", "DR, clustering, anomaly; VLM pipeline and side panel", "100% citation validity on golden set"],
            ["6A VLM decision agent", "VD1–VD12, guards, decision cards, audit", "Zero guard violations; numbers-only fallback"],
            ["6B Catalogue completion", "Every §36, §41 and §42 artefact and the §43 additions", "Every artefact ID renders; every entry has a library"],
            ["7 Enterprise", "Reports, drift monitoring, SSO, Portfolio Lab, optional K8s", "Load and security tests pass"],
            ["8.2 Production hardening", "Time limits, memory guard, AI budgets, heartbeats, backups incl. Storage, observability, deploy guide", "Deployment acceptance criteria pass; every STRESS_TEST item closed"],
          ]}
        />
      </Section>

      <Section heading="Deliverables and open items">
        <NumberedList
          items={[
            "Project kit `ml-lab-project.zip`: `ARCHITECTURE.md` v2.2 (46 sections), `FLOWCHART.md` (20 diagrams), `GAP_AUDIT.md`, `STRESS_TEST.md`, pinned `backend/requirements`, `CURSOR_PROMPT.md` (18 phases with acceptance criteria and an execution protocol), `CURSOR_KICKOFF.md`, Cursor rules, deployment configs, Supabase migrations, sample data and prediction samples.",
            "Prediction samples: 35 files cover all 33 datasets. DS29 is schema-derived (the 260 MB archive was not downloaded), DS32 is synthetic because TradingLab is private, DS33 is synthetic by design. Forecast files hold future dates up to the horizon cap, so DS23 has 9 rows and DS27 has 16.",
            "NVIDIA free API key is a trial for development and testing; production needs a licence or a paid endpoint. Confirm with compliance that aggregate plots and metrics may be sent to the hosted provider.",
            "Cursor model names change often, so the prompt asks for the strongest reasoning model in the picker rather than a fixed name.",
            "Render, Vercel and Supabase prices and limits were read in Nov 2026; re-check before buying.",
            "Intake family weights are starting values and need calibration on a labelled set of datasets.",
            "PBO is not in ml-for-trading; it is designed fresh and must be validated against the original paper.",
            "Suitability thresholds and decision guards are starting values to calibrate on real desk datasets.",
            "Licences to check: TabPFN (v2.5+ weights non-commercial, kept off), model terms on the NVIDIA catalog, and Yahoo Finance data terms for production use.",
            "Stooq rejected (anti-bot page); Yahoo endpoints used instead.",
            "Library versions were checked on PyPI on 15 Nov 2026 (IST) and resolve together for Python 3.12; installing them and checking every API name is a Phase 0 task.",
          ]}
        />
      </Section>
    </Page>
  );
}

