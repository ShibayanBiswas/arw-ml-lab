"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { BatchPredictPanel } from "@/components/predict/BatchPredictPanel";
import { CustomPredictForm } from "@/components/predict/CustomPredictForm";
import {
  getExperiment,
  getJob,
  listModels,
  listSamples,
  loadSample,
  startTrain,
} from "@/lib/api";

type Mode = "home" | "batch" | "custom" | "single";

export function PredictWorkbench({ mode }: { mode: Mode }) {
  const [models, setModels] = useState<
    Array<{ id: string; task: string; target: string | null; dataset_id: string }>
  >([]);
  const [modelId, setModelId] = useState<string>("");
  const [status, setStatus] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [samples, setSamples] = useState<Array<Record<string, unknown>>>([]);

  async function refreshModels() {
    const list = await listModels();
    setModels(list);
    if (!modelId && list[0]) setModelId(list[0].id);
  }

  useEffect(() => {
    void listSamples()
      .then(setSamples)
      .catch((e) => setError(String(e)));
    void refreshModels().catch((e) => setError(String(e)));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function trainDs3() {
    setError(null);
    setStatus("Loading DS3…");
    try {
      const { job_id } = await loadSample("DS3");
      let job = await getJob(job_id);
      while (job.status === "queued" || job.status === "running") {
        await new Promise((r) => setTimeout(r, 200));
        job = await getJob(job_id);
      }
      if (job.status !== "done") throw new Error(job.error || job.status);
      const datasetId = String((job.result as { dataset_id?: string })?.dataset_id ?? "");
      setStatus("Training champion…");
      const started = await startTrain({
        dataset_id: datasetId,
        target: "Survived",
        task: "binary",
        algorithm_keys: ["clf.lgbm"],
      });
      let tj = await getJob(started.job_id);
      while (tj.status === "queued" || tj.status === "running") {
        await new Promise((r) => setTimeout(r, 400));
        tj = await getJob(tj.job_id ?? started.job_id);
      }
      // getJob returns job_id field
      tj = await getJob(started.job_id);
      if (tj.status !== "done") throw new Error(tj.error || tj.status);
      const exp = await getExperiment(started.experiment_id);
      const mid = String((exp.result as { model_id?: string } | undefined)?.model_id ?? "");
      await refreshModels();
      if (mid) setModelId(mid);
      setStatus(mid ? `Ready — model ${mid.slice(0, 8)}…` : "Train done (no model_id — check worker)");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setStatus("");
    }
  }

  const effectiveMode = mode === "single" ? "custom" : mode === "home" ? "chooser" : mode;

  return (
    <div className="mx-auto max-w-5xl p-6">
      <header className="mb-6">
        <h1 className="font-display text-2xl tracking-wide">Prediction Studio</h1>
        <p className="mt-1 text-sm text-[var(--muted)]">
          Batch upload with PV validation, or a contract-driven custom form. Never refits at predict
          time.
        </p>
      </header>

      <section className="mb-4 flex flex-wrap items-end gap-3 rounded border border-[var(--border)] p-3">
        <label className="text-sm">
          Model
          <select
            className="mt-1 block min-w-[16rem] rounded border border-[var(--border)] bg-transparent px-2 py-1"
            value={modelId}
            onChange={(e) => setModelId(e.target.value)}
          >
            <option value="">— select —</option>
            {models.map((m) => (
              <option key={m.id} value={m.id}>
                {m.id.slice(0, 8)}… · {m.task} · {m.dataset_id}
              </option>
            ))}
          </select>
        </label>
        <button
          type="button"
          className="rounded bg-[var(--gold)] px-3 py-1.5 text-sm text-black"
          onClick={() => void trainDs3()}
        >
          Train DS3 champion
        </button>
        <button
          type="button"
          className="rounded border border-[var(--border)] px-3 py-1.5 text-sm"
          onClick={() => void refreshModels().catch((e) => setError(String(e)))}
        >
          Refresh models
        </button>
        {samples.length ? (
          <span className="text-xs text-[var(--muted)]">{samples.length} samples catalogued</span>
        ) : null}
      </section>

      {status ? <p className="mb-2 text-sm text-[var(--muted)]">{status}</p> : null}
      {error ? <p className="mb-2 text-sm text-red-600">{error}</p> : null}

      {effectiveMode === "chooser" ? (
        <div className="grid gap-4 sm:grid-cols-2">
          <Link
            href="/predict/batch"
            className="rounded border border-[var(--border)] p-6 transition hover:border-[var(--gold)]"
          >
            <h2 className="font-display text-lg">Batch</h2>
            <p className="mt-2 text-sm text-[var(--muted)]">
              Download template, upload CSV/XLSX, review PV report, download scored results.
            </p>
          </Link>
          <Link
            href="/predict/single"
            className="rounded border border-[var(--border)] p-6 transition hover:border-[var(--gold)]"
          >
            <h2 className="font-display text-lg">Custom form</h2>
            <p className="mt-2 text-sm text-[var(--muted)]">
              Widgets from the feature contract, live predict (300 ms debounce), SHAP, reset /
              random row.
            </p>
          </Link>
        </div>
      ) : null}

      {!modelId && effectiveMode !== "chooser" ? (
        <p className="text-sm text-[var(--muted)]">Train or select a model to continue.</p>
      ) : null}

      {modelId && effectiveMode === "batch" ? <BatchPredictPanel modelId={modelId} /> : null}
      {modelId && effectiveMode === "custom" ? <CustomPredictForm modelId={modelId} /> : null}
    </div>
  );
}
