"use client";

import { useCallback, useEffect, useState } from "react";
import { createDemoJob, jobEventsUrl } from "@/lib/api";

type Props = {
  /** Bearer token for lab-api; when omitted, uses AUTH_TEST_BYPASS headers in local demos. */
  accessToken?: string | null;
};

export function JobProgress({ accessToken }: Props) {
  const [jobId, setJobId] = useState<string | null>(null);
  const [pct, setPct] = useState(0);
  const [step, setStep] = useState<string>("idle");
  const [status, setStatus] = useState<"idle" | "running" | "done" | "error">("idle");
  const [error, setError] = useState<string | null>(null);

  const start = useCallback(async () => {
    setError(null);
    setStatus("running");
    setPct(0);
    setStep("enqueue");
    try {
      const token = accessToken ?? "test";
      const { job_id } = await createDemoJob(token, `ui-${Date.now()}`);
      setJobId(job_id);
    } catch (err) {
      setStatus("error");
      setError(err instanceof Error ? err.message : "failed to start job");
    }
  }, [accessToken]);

  useEffect(() => {
    if (!jobId) return;
    const url = jobEventsUrl(jobId);
    const es = new EventSource(url, { withCredentials: false });
    // EventSource cannot set Authorization; for local AC we also poll.
    // Prefer fetch stream with Authorization when token present.
    es.close();

    const controller = new AbortController();
    (async () => {
      try {
        const res = await fetch(url, {
          headers: { Authorization: `Bearer ${accessToken ?? "test"}` },
          signal: controller.signal,
        });
        if (!res.ok || !res.body) {
          throw new Error(`SSE ${res.status}`);
        }
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          const chunks = buffer.split("\n\n");
          buffer = chunks.pop() ?? "";
          for (const chunk of chunks) {
            const lines = chunk.split("\n");
            let event = "message";
            let data = "";
            for (const line of lines) {
              if (line.startsWith("event:")) event = line.slice(6).trim();
              if (line.startsWith("data:")) data += line.slice(5).trim();
            }
            if (!data) continue;
            const payload = JSON.parse(data) as {
              pct?: number;
              step?: string;
              message?: string;
            };
            if (typeof payload.pct === "number") setPct(payload.pct);
            if (payload.step) setStep(payload.step);
            if (event === "done") setStatus("done");
            if (event === "error") {
              setStatus("error");
              setError(payload.message ?? "job error");
            }
          }
        }
      } catch (err) {
        if (!controller.signal.aborted) {
          setStatus("error");
          setError(err instanceof Error ? err.message : "SSE failed");
        }
      }
    })();

    return () => controller.abort();
  }, [jobId, accessToken]);

  return (
    <div className="panel-stable panel-luxe rounded-2xl p-4" data-testid="job-progress">
      <div className="mb-3 flex items-center justify-between gap-3">
        <div>
          <p className="section-kicker">Jobs</p>
          <h2 className="section-title">Demo progress</h2>
        </div>
        <button
          type="button"
          className="rounded-lg gold-gradient px-3 py-2 text-sm font-semibold text-[#111]"
          onClick={start}
          disabled={status === "running"}
        >
          Run demo job
        </button>
      </div>
      <div className="status-pill mb-2">
        <span className="live-sync-dot" />
        <span>
          {status} · {step}
          {jobId ? ` · ${jobId.slice(0, 8)}` : ""}
        </span>
      </div>
      <div
        className="h-2 w-full overflow-hidden rounded-full bg-[var(--bg-muted)]"
        role="progressbar"
        aria-valuenow={Math.round(pct * 100)}
        aria-valuemin={0}
        aria-valuemax={100}
      >
        <div
          className="h-full gold-gradient transition-[width] duration-300"
          style={{ width: `${Math.min(100, Math.round(pct * 100))}%` }}
        />
      </div>
      {error ? <p className="mt-2 text-sm text-[var(--danger)]">{error}</p> : null}
    </div>
  );
}
