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
