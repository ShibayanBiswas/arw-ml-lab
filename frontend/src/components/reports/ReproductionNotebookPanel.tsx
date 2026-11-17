"use client";

import { useState } from "react";
import { runReportsNotebook } from "@/lib/api";

const DEMO_FACTS = {
  seed: 42,
  split: "oof",
  note: "demo FACTS only — metrics must come from a real run",
};

export function ReproductionNotebookPanel() {
  const [status, setStatus] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [filename, setFilename] = useState<string | null>(null);

  async function exportNotebook() {
    setError(null);
    setFilename(null);
    setStatus("Exporting…");
    try {
      const res = await runReportsNotebook({
        title: "DS1 Iris reproduction",
        dataset_id: "DS1",
        algorithm_key: "lightgbm",
        facts: DEMO_FACTS,
      });
      const blob = new Blob([res.nbformat_json], { type: "application/x-ipynb+json" });
      const name = "ds1-lightgbm-reproduction.ipynb";
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = name;
      a.click();
      URL.revokeObjectURL(url);
      setFilename(name);
      setStatus(`Downloaded (artefact ${res.id}, seed ${res.seed})`);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setStatus("");
    }
  }

  return (
    <section className="panel-luxe space-y-3 border border-[var(--line)] p-4">
      <h2 className="font-display text-lg text-[var(--ink)]">Reproduction notebook</h2>
      <p className="text-sm text-[var(--muted)]">
        nbformat v4 export via <span className="font-mono text-xs">REP.T.NOTEBOOK</span> (§46.4 /
        ST-UX-02). FACTS are embedded verbatim; the notebook is not executed here.
      </p>
      <button
        type="button"
        className="bg-[var(--gold)] px-3 py-1.5 text-sm text-[var(--ink)]"
        onClick={() => void exportNotebook()}
      >
        Export DS1 demo .ipynb
      </button>
      {status && <p className="text-sm text-[var(--muted)]">{status}</p>}
      {filename && (
        <p className="font-mono text-xs text-[var(--muted)]">
          saved as {filename}
        </p>
      )}
      {error && <p className="text-sm text-red-700">{error}</p>}
    </section>
  );
}