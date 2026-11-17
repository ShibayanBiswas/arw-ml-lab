/** Thin client for lab-api (SSE connects here directly — not via Vercel). */

import { labAuthHeaders } from "@/lib/lab-session";

export function labApiBase(): string {
  return process.env.NEXT_PUBLIC_LAB_API_URL ?? "http://localhost:8000";
}

export async function createDemoJob(token: string, idempotencyKey?: string) {
  const headers: Record<string, string> = {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };
  if (idempotencyKey) headers["Idempotency-Key"] = idempotencyKey;
  const res = await fetch(`${labApiBase()}/api/v1/jobs/demo`, {
    method: "POST",
    headers,
  });
  if (!res.ok) {
    throw new Error(`demo job failed: ${res.status}`);
  }
  return (await res.json()) as { job_id: string };
}

export function jobEventsUrl(jobId: string): string {
  return `${labApiBase()}/api/v1/jobs/${jobId}/events`;
}

export async function listSamples() {
  const res = await fetch(`${labApiBase()}/api/v1/datasets/samples`, {
    headers: labAuthHeaders(),
  });
  if (!res.ok) throw new Error(`samples: ${res.status}`);
  return (await res.json()) as Array<Record<string, unknown>>;
}

export async function loadSample(sampleId: string) {
  const res = await fetch(`${labApiBase()}/api/v1/datasets/samples/${sampleId}/load`, {
    method: "POST",
    headers: labAuthHeaders(),
  });
  if (!res.ok) throw new Error(`load sample: ${res.status}`);
  return (await res.json()) as { job_id: string };
}

export async function getJob(jobId: string) {
  const res = await fetch(`${labApiBase()}/api/v1/jobs/${jobId}`, {
    headers: labAuthHeaders(),
  });
  if (!res.ok) throw new Error(`job: ${res.status}`);
  return (await res.json()) as {
    job_id: string;
    status: string;
    progress: number;
    error?: string;
    result?: Record<string, unknown>;
  };
}

export async function listDatasets() {
  const res = await fetch(`${labApiBase()}/api/v1/datasets`, { headers: labAuthHeaders() });
  if (!res.ok) throw new Error(`datasets: ${res.status}`);
  return (await res.json()) as Array<Record<string, unknown>>;
}

export async function previewDataset(id: string) {
  const res = await fetch(`${labApiBase()}/api/v1/datasets/${id}/preview`, {
    headers: labAuthHeaders(),
  });
  if (!res.ok) throw new Error(`preview: ${res.status}`);
  return (await res.json()) as Record<string, unknown>;
}

export async function runEda(datasetId: string) {
  const res = await fetch(`${labApiBase()}/api/v1/eda/${datasetId}/run`, {
    method: "POST",
    headers: labAuthHeaders(),
  });
  if (!res.ok) throw new Error(`eda: ${res.status}`);
  return (await res.json()) as { job_id: string };
}

export async function getEdaByJob(jobId: string) {
  const res = await fetch(`${labApiBase()}/api/v1/eda/by-job/${jobId}`, {
    headers: labAuthHeaders(),
  });
  if (!res.ok) throw new Error(`eda by job: ${res.status}`);
  return (await res.json()) as {
    id: string;
    status: string;
    summary: Record<string, unknown>;
    insights: Array<{
      rule_id: string;
      severity: "info" | "warning" | "critical";
      message: string;
      column?: string | null;
      value?: number | null;
    }>;
    artefacts: Array<Record<string, unknown>>;
  };
}

export async function uploadDataset(file: File) {
  const form = new FormData();
  form.append("file", file);
  const headers = labAuthHeaders();
  delete headers["Content-Type"];
  const res = await fetch(`${labApiBase()}/api/v1/datasets/direct-upload`, {
    method: "POST",
    headers,
    body: form,
  });
  if (!res.ok) throw new Error(`upload: ${res.status}`);
  return (await res.json()) as { job_id: string; dataset_id: string };
}

export async function getIntake(versionId: string) {
  const res = await fetch(`${labApiBase()}/api/v1/intake/${versionId}`, {
    headers: labAuthHeaders(),
  });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`intake: ${res.status}`);
  return (await res.json()) as Record<string, unknown> & { id: string };
}

export async function runIntake(versionId: string) {
  const res = await fetch(`${labApiBase()}/api/v1/intake/${versionId}/run`, {
    method: "POST",
    headers: { ...labAuthHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify({ use_llm: false }),
  });
  if (!res.ok) throw new Error(`intake run: ${res.status}`);
  return (await res.json()) as { job_id: string };
}

export async function patchIntake(proposalId: string, overrides: Record<string, unknown>) {
  const res = await fetch(`${labApiBase()}/api/v1/intake/proposals/${proposalId}`, {
    method: "PATCH",
    headers: { ...labAuthHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify({ overrides }),
  });
  if (!res.ok) throw new Error(`intake patch: ${res.status}`);
  return (await res.json()) as Record<string, unknown>;
}

export async function confirmIntake(proposalId: string, experimentName?: string) {
  const res = await fetch(`${labApiBase()}/api/v1/intake/proposals/${proposalId}/confirm`, {
    method: "POST",
    headers: { ...labAuthHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify({ experiment_name: experimentName }),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`intake confirm: ${res.status} ${detail}`);
  }
  return (await res.json()) as { experiment_id: string; task_spec: Record<string, unknown> };
}

export async function startTrain(body: {
  dataset_id: string;
  target: string;
  task: string;
  algorithm_keys?: string[];
  cv_scheme?: string;
  tuning_preset?: string;
}) {
  const res = await fetch(`${labApiBase()}/api/v1/experiments/train`, {
    method: "POST",
    headers: { ...labAuthHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`train: ${res.status}`);
  return (await res.json()) as { job_id: string; experiment_id: string };
}

export async function startTune(body: {
  dataset_id: string;
  target: string;
  algorithm_key: string;
  task: string;
  preset?: string;
  n_trials?: number;
  fixed_params?: Record<string, unknown>;
}) {
  const res = await fetch(`${labApiBase()}/api/v1/experiments/tune`, {
    method: "POST",
    headers: { ...labAuthHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`tune: ${res.status}`);
  return (await res.json()) as { job_id: string; experiment_id: string };
}

export async function getExperiment(experimentId: string) {
  const res = await fetch(`${labApiBase()}/api/v1/experiments/${experimentId}`, {
    headers: labAuthHeaders(),
  });
  if (!res.ok) throw new Error(`experiment: ${res.status}`);
  return (await res.json()) as {
    id: string;
    status: string;
    leaderboard: Array<Record<string, unknown>>;
    result?: Record<string, unknown>;
    eval?: Record<string, unknown>;
    champion?: { algorithm_key?: string };
  };
}

export type FeatureContract = {
  contract_version?: string;
  dataset_id?: string;
  task?: string;
  target?: string | null;
  features?: Array<{
    name: string;
    kind: string;
    dtype?: string;
    nullable?: boolean;
    role?: string;
    min?: number | null;
    max?: number | null;
    median?: number | null;
    p01?: number | null;
    p99?: number | null;
    integer?: boolean;
    categories?: string[] | null;
    mode?: string | null;
  }>;
  [key: string]: unknown;
};

export async function listModels() {
  const res = await fetch(`${labApiBase()}/api/v1/models`, { headers: labAuthHeaders() });
  if (!res.ok) throw new Error(`models: ${res.status}`);
  return (await res.json()) as Array<{
    id: string;
    task: string;
    target: string | null;
    dataset_id: string;
    n_features: number;
    meta?: Record<string, unknown>;
  }>;
}

export async function getModelSchema(modelId: string) {
  const res = await fetch(`${labApiBase()}/api/v1/models/${modelId}/schema`, {
    headers: labAuthHeaders(),
  });
  if (!res.ok) throw new Error(`schema: ${res.status}`);
  return (await res.json()) as FeatureContract;
}

export async function getModelSampleRow(modelId: string) {
  const res = await fetch(`${labApiBase()}/api/v1/models/${modelId}/sample-row`, {
    headers: labAuthHeaders(),
  });
  if (!res.ok) throw new Error(`sample-row: ${res.status}`);
  return (await res.json()) as { row: Record<string, unknown>; feature_names: string[] };
}

export function modelTemplateUrl(modelId: string, format: "csv" | "xlsx" = "csv") {
  return `${labApiBase()}/api/v1/models/${modelId}/template?format=${format}`;
}

export async function downloadModelTemplate(modelId: string, format: "csv" | "xlsx" = "csv") {
  const res = await fetch(modelTemplateUrl(modelId, format), { headers: labAuthHeaders() });
  if (!res.ok) throw new Error(`template: ${res.status}`);
  return res.blob();
}

export async function predictSingle(modelId: string, row: Record<string, unknown>) {
  const res = await fetch(`${labApiBase()}/api/v1/models/${modelId}/predict`, {
    method: "POST",
    headers: labAuthHeaders(),
    body: JSON.stringify({ row }),
  });
  if (!res.ok) throw new Error(`predict: ${res.status}`);
  return (await res.json()) as {
    prediction: unknown;
    probabilities?: number[];
    n_rows: number;
    refit: boolean;
  };
}

export async function predictBatchJson(modelId: string, rows: Record<string, unknown>[]) {
  const res = await fetch(`${labApiBase()}/api/v1/predict/batch`, {
    method: "POST",
    headers: labAuthHeaders(),
    body: JSON.stringify({ model_id: modelId, rows }),
  });
  if (!res.ok) throw new Error(`predict batch: ${res.status}`);
  return (await res.json()) as {
    validation: Record<string, unknown>;
    scored: boolean;
    predictions?: unknown[];
    probabilities?: number[][];
    csv?: string | null;
    n_rows?: number;
    refit?: boolean;
  };
}

export async function predictBatchUpload(modelId: string, file: File) {
  const form = new FormData();
  form.append("model_id", modelId);
  form.append("file", file);
  const headers = labAuthHeaders();
  delete headers["Content-Type"];
  const res = await fetch(`${labApiBase()}/api/v1/predict/batch/upload`, {
    method: "POST",
    headers,
    body: form,
  });
  if (!res.ok) throw new Error(`predict upload: ${res.status}`);
  return (await res.json()) as {
    validation: Record<string, unknown>;
    scored: boolean;
    predictions?: unknown[];
    probabilities?: number[][];
    csv?: string | null;
    n_rows?: number;
    refit?: boolean;
  };
}

export async function explainRows(
  modelId: string,
  rows: Record<string, unknown>[],
  method: "shap" | "permutation" | "lime" | "dice" | "ale" = "shap",
  targetValues?: unknown[],
  aleFeature?: string
) {
  const res = await fetch(`${labApiBase()}/api/v1/explain/${modelId}`, {
    method: "POST",
    headers: { ...labAuthHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify({
      rows,
      method,
      ...(targetValues !== undefined ? { target_values: targetValues } : {}),
      ...(aleFeature !== undefined ? { ale_feature: aleFeature } : {}),
    }),
  });
  if (!res.ok) throw new Error(`explain: ${res.status}`);
  return (await res.json()) as Record<string, unknown>;
}

export async function permutationExplain(
  modelId: string,
  rows: Record<string, unknown>[],
  targetValues: unknown[]
) {
  return explainRows(modelId, rows, "permutation", targetValues);
}

export type UnsupervisedRunBody = {
  rows: Record<string, unknown>[];
  algorithm: string;
  n_clusters?: number;
  n_components?: number;
  contamination?: number;
  seed?: number;
  top_n?: number;
};

export type AnomalyCataloguePlot =
  | "score-hist"
  | "ranked"
  | "embed"
  | "pareto"
  | "pairwise";

export type ClusteringCataloguePlot =
  | "elbow"
  | "silhouette"
  | "ch"
  | "db"
  | "gap"
  | "dendrogram"
  | "k-sweep"
  | "clustermap"
  | "reachability"
  | "k-distance";

export type DrCataloguePlot =
  | "scree"
  | "cumvar"
  | "biplot"
  | "loadings"
  | "correlation-circle"
  | "shepard";

export function unsupervisedAnomalyPlotPath(plot: AnomalyCataloguePlot): string {
  return `/api/v1/unsupervised/anomaly/${plot}`;
}

export function unsupervisedClusteringPlotPath(plot: ClusteringCataloguePlot): string {
  return `/api/v1/unsupervised/clustering/${plot}`;
}

export function unsupervisedDrPlotPath(plot: DrCataloguePlot): string {
  return `/api/v1/unsupervised/dr/${plot}`;
}

export async function runUnsupervised(
  family: "clustering" | "dr" | "anomaly",
  body: UnsupervisedRunBody
) {
  const res = await fetch(`${labApiBase()}/api/v1/unsupervised/${family}`, {
    method: "POST",
    headers: { ...labAuthHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`unsupervised ${family}: ${res.status} ${detail}`);
  }
  return (await res.json()) as Record<string, unknown>;
}

export async function runUnsupervisedAnomalyPlot(
  plot: AnomalyCataloguePlot,
  body: UnsupervisedRunBody
) {
  const res = await fetch(`${labApiBase()}${unsupervisedAnomalyPlotPath(plot)}`, {
    method: "POST",
    headers: { ...labAuthHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify({ ...body, seed: body.seed ?? 42 }),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`anomaly plot ${plot}: ${res.status} ${detail}`);
  }
  return (await res.json()) as Record<string, unknown>;
}

export async function runUnsupervisedClusteringPlot(
  plot: ClusteringCataloguePlot,
  body: UnsupervisedRunBody
) {
  const res = await fetch(`${labApiBase()}${unsupervisedClusteringPlotPath(plot)}`, {
    method: "POST",
    headers: { ...labAuthHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify({ ...body, seed: body.seed ?? 42 }),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`clustering plot ${plot}: ${res.status} ${detail}`);
  }
  return (await res.json()) as Record<string, unknown>;
}

export async function runUnsupervisedDrPlot(plot: DrCataloguePlot, body: UnsupervisedRunBody) {
  const res = await fetch(`${labApiBase()}${unsupervisedDrPlotPath(plot)}`, {
    method: "POST",
    headers: { ...labAuthHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify({ ...body, seed: body.seed ?? 42 }),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`dr plot ${plot}: ${res.status} ${detail}`);
  }
  return (await res.json()) as Record<string, unknown>;
}

export type SuitabilityCataloguePlot =
  | "volatility"
  | "price"
  | "barriers"
  | "uniqueness"
  | "holding"
  | "min-ffd"
  | "sadf"
  | "trendscan"
  | "label-balance"
  | "grid";

export type SuitabilityPlotBody = {
  sample_id?: string;
  rows?: Record<string, unknown>[];
  time_col?: string;
  asset?: string;
  price_col?: string;
  vol_span?: number;
  horizon?: number;
  pt_mult?: number;
  sl_mult?: number;
  n_samples?: number;
  cusum_mult?: number;
  d_step?: number;
  min_window?: number;
  max_lookback?: number;
  sadf_maxlag?: number;
  sadf_end_step?: number;
  trendscan_l_min?: number;
  trendscan_l_max?: number;
  trendscan_step?: number;
  label_method?: "triple_barrier" | "fixed_horizon";
};

export function suitabilityPlotPath(plot: SuitabilityCataloguePlot): string {
  return `/api/v1/suitability/plots/${plot}`;
}

export async function runSuitability(body: SuitabilityPlotBody) {
  const res = await fetch(`${labApiBase()}/api/v1/suitability/run`, {
    method: "POST",
    headers: { ...labAuthHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`suitability: ${res.status} ${detail}`);
  }
  return (await res.json()) as Record<string, unknown>;
}

export async function runSuitabilityPlot(
  plot: SuitabilityCataloguePlot,
  body: SuitabilityPlotBody
) {
  const res = await fetch(`${labApiBase()}${suitabilityPlotPath(plot)}`, {
    method: "POST",
    headers: { ...labAuthHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`suitability plot ${plot}: ${res.status} ${detail}`);
  }
  return (await res.json()) as Record<string, unknown>;
}

export async function tsHorizon(body: {
  sample_id?: string;
  n?: number;
  freq?: string;
  m?: number;
  h_request?: number;
}) {
  const res = await fetch(`${labApiBase()}/api/v1/timeseries/horizon`, {
    method: "POST",
    headers: labAuthHeaders(),
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`horizon: ${res.status} ${detail}`);
  }
  return (await res.json()) as {
    h_max: number;
    h_default: number;
    reasons: string[];
    disabled_models: Array<{ model: string; reason: string }>;
    request_allowed?: boolean;
  };
}

export async function tsBacktest(body: {
  sample_id?: string;
  h: number;
  w?: number;
  m?: number;
  freq?: string;
}) {
  const res = await fetch(`${labApiBase()}/api/v1/timeseries/backtest`, {
    method: "POST",
    headers: labAuthHeaders(),
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`backtest: ${res.status} ${detail}`);
  }
  return (await res.json()) as Record<string, unknown>;
}

export async function tsAnalysis(body: { sample_id?: string; m?: number }) {
  const res = await fetch(`${labApiBase()}/api/v1/timeseries/analysis`, {
    method: "POST",
    headers: labAuthHeaders(),
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`analysis: ${res.status}`);
  return (await res.json()) as Record<string, unknown>;
}

export type MonitoringKsBody = {
  reference: number[][];
  current: number[][];
  feature_names?: string[];
  alpha?: number;
};

export function monitoringKsDriftPath(): string {
  return "/api/v1/monitoring/drift/ks";
}

export async function runMonitoringKsDrift(body: MonitoringKsBody) {
  const res = await fetch(`${labApiBase()}${monitoringKsDriftPath()}`, {
    method: "POST",
    headers: { ...labAuthHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`monitoring ks: ${res.status} ${detail}`);
  }
  return (await res.json()) as Record<string, unknown>;
}
