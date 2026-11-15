/** ML Lab module registry — ARCHITECTURE §5.2 (SP ModuleGroup/NavItem pattern, no embedBase). */

export type TaskFamily = "supervised" | "unsupervised" | "timeseries" | "any";

export type NavItem = {
  id: string;
  label: string;
  description?: string;
  path?: string;
  children?: NavItem[];
};

export type ModuleGroup = {
  id: string;
  label: string;
  description: string;
  icon:
    | "database"
    | "chart"
    | "sliders"
    | "brain"
    | "layers"
    | "lineChart"
    | "search"
    | "sparkles"
    | "flask"
    | "fileText"
    | "graduation"
    | "shield";
  href: string;
  routeSlug: string;
  requires: TaskFamily[];
  nav: NavItem[];
};

function leaves(
  base: string,
  items: { id: string; label: string; description?: string }[]
): NavItem[] {
  return items.map((item) => ({
    id: item.id,
    label: item.label,
    description: item.description,
    path: `${base}/${item.id}`,
  }));
}

export const MODULES: ModuleGroup[] = [
  {
    id: "data",
    label: "Data",
    description: "Upload, samples, schema and versions",
    icon: "database",
    href: "/data",
    routeSlug: "data",
    requires: ["any"],
    nav: leaves("/data", [
      { id: "home", label: "Home" },
      { id: "upload", label: "Upload" },
      { id: "samples", label: "Sample Datasets" },
      { id: "explorer", label: "Explorer" },
      { id: "schema", label: "Schema & Types" },
      { id: "versions", label: "Versions" },
      { id: "joins", label: "Joins/Merge" },
    ]),
  },
  {
    id: "eda",
    label: "EDA",
    description: "Exploratory data analysis",
    icon: "chart",
    href: "/eda",
    routeSlug: "eda",
    requires: ["any"],
    nav: leaves("/eda", [
      { id: "home", label: "Home" },
      { id: "overview", label: "Overview" },
      { id: "univariate", label: "Univariate" },
      { id: "bivariate", label: "Bivariate" },
      { id: "multivariate", label: "Multivariate" },
      { id: "missingness", label: "Missingness" },
      { id: "outliers", label: "Outliers" },
      { id: "target", label: "Target Analysis" },
      { id: "correlation", label: "Correlation & Dependence" },
      { id: "sequential", label: "Sequential/Temporal" },
      { id: "quality", label: "Data Quality" },
      { id: "report", label: "Report" },
    ]),
  },
  {
    id: "preprocess",
    label: "Preprocess",
    description: "Recipes, encoding, scaling",
    icon: "sliders",
    href: "/preprocess",
    routeSlug: "preprocess",
    requires: ["supervised", "unsupervised", "timeseries"],
    nav: leaves("/preprocess", [
      { id: "home", label: "Home" },
      { id: "recipe", label: "Recipe Builder" },
      { id: "imputation", label: "Imputation" },
      { id: "encoding", label: "Encoding" },
      { id: "scaling", label: "Scaling & Transforms" },
      { id: "outliers", label: "Outliers" },
      { id: "features", label: "Feature Engineering" },
      { id: "selection", label: "Feature Selection" },
      { id: "imbalance", label: "Imbalance" },
      { id: "financial", label: "Financial Features" },
      { id: "leakage", label: "Leakage Check" },
      { id: "preview", label: "Preview" },
    ]),
  },
  {
    id: "supervised",
    label: "Supervised",
    description: "Regression, classification, sequential",
    icon: "brain",
    href: "/supervised",
    routeSlug: "supervised",
    requires: ["supervised"],
    nav: leaves("/supervised", [
      { id: "home", label: "Home" },
      { id: "task", label: "Task Setup" },
      { id: "lab", label: "Model Lab" },
      { id: "cv", label: "CV & Tuning" },
      { id: "runs", label: "Runs" },
      { id: "leaderboard", label: "Leaderboard" },
      { id: "detail", label: "Model Detail" },
      { id: "compare", label: "Compare" },
      { id: "ensembles", label: "Ensembles" },
      { id: "backtest", label: "Financial Backtest" },
    ]),
  },
  {
    id: "unsupervised",
    label: "Unsupervised",
    description: "DR, clustering, anomaly",
    icon: "layers",
    href: "/unsupervised",
    routeSlug: "unsupervised",
    requires: ["unsupervised"],
    nav: leaves("/unsupervised", [
      { id: "home", label: "Home" },
      { id: "setup", label: "Setup" },
      { id: "dr", label: "Dimensionality Reduction" },
      { id: "clustering", label: "Clustering" },
      { id: "anomaly", label: "Anomaly Detection" },
      { id: "selection", label: "Model Selection" },
      { id: "profiles", label: "Profiles" },
      { id: "compare", label: "Compare" },
    ]),
  },
  {
    id: "timeseries",
    label: "Time Series",
    description: "Analysis and forecasting",
    icon: "lineChart",
    href: "/timeseries",
    routeSlug: "timeseries",
    requires: ["timeseries"],
    nav: leaves("/timeseries", [
      { id: "home", label: "Home" },
      { id: "setup", label: "Setup" },
      { id: "analysis", label: "Analysis" },
      { id: "lab", label: "Model Lab" },
      { id: "backtesting", label: "Backtesting" },
      { id: "leaderboard", label: "Leaderboard" },
      { id: "forecast", label: "Forecast" },
      { id: "residuals", label: "Residual Diagnostics" },
      { id: "multivariate", label: "Multivariate" },
    ]),
  },
  {
    id: "explain",
    label: "Explain",
    description: "Global and local explainability",
    icon: "search",
    href: "/explain",
    routeSlug: "explain",
    requires: ["supervised", "unsupervised", "timeseries"],
    nav: leaves("/explain", [
      { id: "home", label: "Home" },
      { id: "global", label: "Global" },
      { id: "local", label: "Local" },
      { id: "interactions", label: "Interactions" },
      { id: "financial", label: "Financial FI" },
      { id: "compare", label: "Compare" },
    ]),
  },
  {
    id: "predict",
    label: "Predict",
    description: "Prediction Studio",
    icon: "sparkles",
    href: "/predict",
    routeSlug: "predict",
    requires: ["supervised", "unsupervised", "timeseries"],
    nav: leaves("/predict", [
      { id: "home", label: "Home" },
      { id: "single", label: "Single" },
      { id: "batch", label: "Batch" },
      { id: "what-if", label: "What-if / Scenario" },
      { id: "forecast", label: "Forecast" },
      { id: "monitoring", label: "Monitoring" },
      { id: "api", label: "API" },
    ]),
  },
  {
    id: "experiments",
    label: "Experiments",
    description: "Runs, registry, lineage",
    icon: "flask",
    href: "/experiments",
    routeSlug: "experiments",
    requires: ["any"],
    nav: leaves("/experiments", [
      { id: "home", label: "Home" },
      { id: "runs", label: "Runs table" },
      { id: "compare", label: "Compare runs" },
      { id: "registry", label: "Registry" },
      { id: "lineage", label: "Lineage" },
      { id: "artifacts", label: "Artifacts" },
    ]),
  },
  {
    id: "reports",
    label: "Reports",
    description: "Report builder and history",
    icon: "fileText",
    href: "/reports",
    routeSlug: "reports",
    requires: ["any"],
    nav: leaves("/reports", [
      { id: "home", label: "Home" },
      { id: "builder", label: "Builder" },
      { id: "templates", label: "Templates" },
      { id: "history", label: "History" },
    ]),
  },
  {
    id: "learn",
    label: "Learn",
    description: "Logic Atlas",
    icon: "graduation",
    href: "/learn",
    routeSlug: "learn",
    requires: ["any"],
    nav: leaves("/learn", [
      { id: "algorithms", label: "Algorithms" },
      { id: "metrics", label: "Metrics" },
      { id: "plots", label: "Plots" },
      { id: "tests", label: "Tests" },
      { id: "encodings", label: "Encodings" },
      { id: "cv", label: "CV" },
      { id: "glossary", label: "Glossary" },
    ]),
  },
  {
    id: "admin",
    label: "Admin",
    description: "Users, quotas, workers, audit",
    icon: "shield",
    href: "/admin",
    routeSlug: "admin",
    requires: ["any"],
    nav: leaves("/admin", [
      { id: "users", label: "Users & Roles" },
      { id: "workspaces", label: "Workspaces" },
      { id: "quotas", label: "Quotas" },
      { id: "workers", label: "Workers & Queues" },
      { id: "vlm", label: "VLM settings" },
      { id: "audit", label: "Audit log" },
      { id: "health", label: "System health" },
    ]),
  },
];

/** 13 entries: Home Terminal (sidebar link) + 12 MODULES groups. */
export const MODULE_COUNT = MODULES.length + 1;

export function collectNavPaths(item: NavItem): string[] {
  const paths: string[] = [];
  if (item.path) paths.push(item.path);
  for (const child of item.children ?? []) {
    paths.push(...collectNavPaths(child));
  }
  return paths;
}
