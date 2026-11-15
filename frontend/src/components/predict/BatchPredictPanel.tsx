"use client";

import { useState } from "react";
import { downloadModelTemplate, labApiBase, predictBatchUpload } from "@/lib/api";
import { labAuthHeaders } from "@/lib/lab-session";

type Props = {
  modelId: string;
};

type PvItem = {
  code?: string;
  severity?: string;
  message?: string;
  column?: string | null;
  n_rows?: number | null;
};

export function BatchPredictPanel({ modelId }: Props) {
  const [status, setStatus] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [validation, setValidation] = useState<Record<string, unknown> | null>(null);
  const [csv, setCsv] = useState<string | null>(null);
  const [nRows, setNRows] = useState<number | null>(null);

  async function onDownloadTemplate() {
    setError(null);
    try {
      const blob = await downloadModelTemplate(modelId, "csv");
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `predict_template_${modelId.slice(0, 8)}.csv`;
      a.click();
      URL.revokeObjectURL(url);
      setStatus("Template downloaded");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }

  async function onUpload(file: File) {
    setError(null);
    setStatus("Validating & scoring…");
    setValidation(null);
    setCsv(null);
    try {
      const out = await predictBatchUpload(modelId, file);
      setValidation(out.validation);
      setCsv(out.csv ?? null);
      setNRows(out.n_rows ?? null);
      setStatus(out.scored ? `Scored ${out.n_rows ?? "—"} rows` : "Validation blocked scoring");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setStatus("");
    }
  }

  async function onLoadSampleCsv() {
    setError(null);
    setStatus("Scoring DS3 predict sample…");
    try {
      const res = await fetch(
        `${labApiBase()}/api/v1/predict/batch/sample/DS3?model_id=${encodeURIComponent(modelId)}`,
        { method: "POST", headers: labAuthHeaders() }
      );
      if (!res.ok) throw new Error(`sample score: ${res.status}`);
      const out = (await res.json()) as {
        validation: Record<string, unknown>;
        scored: boolean;
        csv?: string | null;
        n_rows?: number;
      };
      setValidation(out.validation);
      setCsv(out.csv ?? null);
      setNRows(out.n_rows ?? null);
      setStatus(out.scored ? `Scored ${out.n_rows ?? "—"} rows` : "Validation blocked scoring");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setStatus("");
    }
  }

  function downloadResults() {
    if (!csv) return;
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `predictions_${modelId.slice(0, 8)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  const blocking = (validation?.blocking as PvItem[] | undefined) ?? [];
  const warnings = (validation?.warnings as PvItem[] | undefined) ?? [];

  return (
    <div className="space-y-4 p-4">
      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          className="rounded border border-[var(--border)] px-3 py-1.5 text-sm hover:bg-[var(--surface-2)]"
          onClick={() => void onDownloadTemplate()}
        >
          Download template CSV
        </button>
        <label className="cursor-pointer rounded border border-[var(--border)] px-3 py-1.5 text-sm hover:bg-[var(--surface-2)]">
          Upload CSV / XLSX
          <input
            type="file"
            accept=".csv,.tsv,.xlsx,.xls"
            className="hidden"
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) void onUpload(f);
            }}
          />
        </label>
        <button
          type="button"
          className="rounded border border-[var(--border)] px-3 py-1.5 text-sm hover:bg-[var(--surface-2)]"
          onClick={() => void onLoadSampleCsv()}
        >
          Score DS3 sample (API)
        </button>
        {csv ? (
          <button
            type="button"
            className="rounded bg-[var(--gold)] px-3 py-1.5 text-sm text-black"
            onClick={downloadResults}
          >
            Download results CSV
          </button>
        ) : null}
      </div>
      {status ? <p className="text-sm text-[var(--muted)]">{status}</p> : null}
      {error ? <p className="text-sm text-red-600">{error}</p> : null}
      {validation ? (
        <div className="space-y-2 rounded border border-[var(--border)] p-3 text-sm">
          <p>
            Validation: {validation.ok ? "ok" : "blocked"}
            {nRows != null ? ` · ${nRows} rows scored` : ""}
          </p>
          {blocking.length > 0 ? (
            <ul className="list-disc pl-5 text-red-700">
              {blocking.map((b, i) => (
                <li key={`b-${i}`}>
                  {b.code}: {b.message}
                </li>
              ))}
            </ul>
          ) : null}
          {warnings.length > 0 ? (
            <ul className="list-disc pl-5 text-amber-700">
              {warnings.map((w, i) => (
                <li key={`w-${i}`}>
                  {w.code}: {w.message}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-[var(--muted)]">No blocking PVs</p>
          )}
        </div>
      ) : null}
    </div>
  );
}
