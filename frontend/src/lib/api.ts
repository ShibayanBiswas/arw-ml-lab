/** Thin client for lab-api (SSE connects here directly — not via Vercel). */

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
