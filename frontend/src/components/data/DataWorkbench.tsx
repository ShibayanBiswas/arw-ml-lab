"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  getJob,
  listDatasets,
  listSamples,
  loadSample,
  previewDataset,
  uploadDataset,
} from "@/lib/api";

type Mode = "upload" | "samples" | "explorer" | "schema" | "joins";

export function DataWorkbench({ mode }: { mode: Mode }) {
  const router = useRouter();
  const [samples, setSamples] = useState<Array<Record<string, unknown>>>([]);
  const [datasets, setDatasets] = useState<Array<Record<string, unknown>>>([]);
  const [preview, setPreview] = useState<Record<string, unknown> | null>(null);
  const [status, setStatus] = useState<string>("");
  const [error, setError] = useState<string>("");

  const refresh = useCallback(async () => {
    try {
      setDatasets(await listDatasets());
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }, []);

  useEffect(() => {
    if (mode === "samples") {
      listSamples()
        .then(setSamples)
        .catch((e) => setError(String(e)));
    }
    if (mode === "explorer" || mode === "schema") {
      void refresh();
    }
  }, [mode, refresh]);

  async function onLoadSample(id: string) {
    setStatus(`Loading ${id}…`);
    setError("");
    try {
      const { job_id } = await loadSample(id);
      let job = await getJob(job_id);
      while (job.status === "queued" || job.status === "running") {
        await new Promise((r) => setTimeout(r, 200));
        job = await getJob(job_id);
      }
      if (job.status !== "done") throw new Error(job.status);
      const dsId = String(job.result?.dataset_id ?? "");
      setStatus(`Loaded ${id} → ${dsId}`);
      await refresh();
      if (dsId) {
        setPreview(await previewDataset(dsId));
        router.push(`/data/intake-review?version=${dsId}`);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setStatus("");
    }
  }

  async function onUpload(file: File | null) {
    if (!file) return;
    setStatus(`Uploading ${file.name}…`);
    setError("");
    try {
      const { job_id, dataset_id } = await uploadDataset(file);
      let job = await getJob(job_id);
      while (job.status === "queued" || job.status === "running") {
        await new Promise((r) => setTimeout(r, 200));
        job = await getJob(job_id);
      }
      setStatus(`Ingested ${dataset_id}`);
      await refresh();
      setPreview(await previewDataset(dataset_id));
      router.push(`/data/intake-review?version=${dataset_id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }

  return (
    <div className="space-y-4">
      <section className="panel-stable panel-luxe animate-rise rounded-2xl p-6">
        <p className="section-kicker">Data</p>
        <h1 className="section-title mt-1">
          {mode === "upload"
            ? "Upload"
            : mode === "samples"
              ? "Sample datasets"
              : mode === "schema"
                ? "Schema & types"
                : "Explorer"}
        </h1>
        {status ? <p className="mt-2 text-sm text-[var(--gold)]">{status}</p> : null}
        {error ? <p className="mt-2 text-sm text-red-600">{error}</p> : null}
      </section>

      {mode === "upload" ? (
        <section className="panel-stable rounded-2xl p-6">
          <label className="block text-sm text-[var(--fg-muted)]">
            CSV / TSV / XLSX / Parquet
            <input
              type="file"
              className="mt-2 block w-full text-sm"
              accept=".csv,.tsv,.xlsx,.xls,.parquet,.feather,.jsonl"
              onChange={(e) => void onUpload(e.target.files?.[0] ?? null)}
            />
          </label>
        </section>
      ) : null}

      {mode === "samples" ? (
        <section className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {samples.map((s) => (
            <button
              key={String(s.id)}
              type="button"
              className="panel-stable rounded-2xl p-4 text-left hover:border-[var(--gold)]"
              onClick={() => void onLoadSample(String(s.id))}
            >
              <p className="font-mono text-xs text-[var(--gold)]">{String(s.id)}</p>
              <p className="mt-1 font-[family-name:var(--font-display)] text-lg">{String(s.name)}</p>
              <p className="mt-1 text-xs text-[var(--fg-muted)]">
                {String(s.family)} · {String(s.task)} · target {String(s.target)}
              </p>
            </button>
          ))}
        </section>
      ) : null}

      {(mode === "explorer" || mode === "schema") && (
        <section className="panel-stable rounded-2xl p-4">
          <h2 className="mb-3 text-sm font-medium">Datasets</h2>
          <ul className="space-y-2">
            {datasets.map((d) => (
              <li key={String(d.id)}>
                <button
                  type="button"
                  className="w-full rounded-lg border border-[var(--border)] px-3 py-2 text-left text-sm hover:border-[var(--gold)]"
                  onClick={() => void previewDataset(String(d.id)).then(setPreview)}
                >
                  <span className="font-mono text-xs text-[var(--fg-muted)]">{String(d.id).slice(0, 8)}</span>{" "}
                  {String(d.name)}
                </button>
              </li>
            ))}
          </ul>
        </section>
      )}

      {preview ? (
        <section className="panel-stable rounded-2xl p-4">
          <h2 className="text-sm font-medium">Preview · {String(preview.name)}</h2>
          {mode === "schema" ? (
            <pre className="mt-3 max-h-96 overflow-auto text-xs">
              {JSON.stringify(preview.schema, null, 2)}
            </pre>
          ) : (
            <pre className="mt-3 max-h-96 overflow-auto text-xs">
              {JSON.stringify(preview.preview, null, 2)}
            </pre>
          )}
        </section>
      ) : null}
    </div>
  );
}
