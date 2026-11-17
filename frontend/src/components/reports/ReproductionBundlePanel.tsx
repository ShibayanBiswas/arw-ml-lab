"use client";

import { useState } from "react";
import { runReportsBundle } from "@/lib/api";

const DEMO_FACTS = {
  seed: 42,
  split: "oof",
  note: "demo FACTS only — bundle hashes config, not row data",
};

export function ReproductionBundlePanel() {
  const [status, setStatus] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [filename, setFilename] = useState<string | null>(null);

  async function exportBundle() {
    setError(null);
    setFilename(null);
    setStatus("Packing…");
    try {
      const res = await runReportsBundle({
        title: "DS1 Iris reproduction",
        dataset_id: "DS1",
        algorithm_key: "lightgbm",
        facts: DEMO_FACTS,
      });
      const bytes = Uint8Array.from(atob(res.zip_base64), (c) => c.charCodeAt(0));
      const blob = new Blob([bytes], { type: "application/zip" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = res.filename;
      a.click();
      URL.revokeObjectURL(url);
      setFilename(res.filename);
      setStatus(`Downloaded (${res.id}, ${res.timezone}, seed ${res.seed})`);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setStatus("");
    }
  }

  return (
    <section className="panel-luxe space-y-3 border border-[var(--line)] p-4">
      <h2 className="font-display text-lg text-[var(--ink)]">Reproduction bundle</h2>
      <p className="text-sm text-[var(--muted)]">
        Zip export via <span className="font-mono text-xs">REP.T.BUNDLE</span> (ST-UX-02): config,
        data hash, notebook, core pins and a stub script. Times in manifest use IST (
        <span className="font-mono text-xs">Asia/Kolkata</span>).
      </p>
      <button
        type="button"
        className="bg-[var(--gold)] px-3 py-1.5 text-sm text-[var(--ink)]"
        onClick={() => void exportBundle()}
      >
        Export DS1 demo .zip
      </button>
      {status && <p className="text-sm text-[var(--muted)]">{status}</p>}
      {filename && (
        <p className="font-mono text-xs text-[var(--muted)]">saved as {filename}</p>
      )}
      {error && <p className="text-sm text-red-700">{error}</p>}
    </section>
  );
}