"use client";

import { useState } from "react";
import { runUnsupervised } from "@/lib/api";

type Mode = "home" | "setup" | "dr" | "clustering" | "anomaly" | "selection" | "profiles" | "compare";

const DEMO_ROWS = Array.from({ length: 40 }, (_, i) => ({
  x: Math.sin(i / 5) + (i % 7) * 0.1,
  y: Math.cos(i / 4) + (i % 5) * 0.15,
  z: i * 0.02,
}));

export function UnsupervisedWorkbench({ mode }: { mode: Mode }) {
  const family =
    mode === "dr" ? "dr" : mode === "anomaly" ? "anomaly" : "clustering";
  const [algorithm, setAlgorithm] = useState(
    family === "dr" ? "pca" : family === "anomaly" ? "isolation_forest" : "kmeans"
  );
  const [status, setStatus] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);

  async function run() {
    setError(null);
    setStatus(`Running ${family}/${algorithm}…`);
    try {
      const out = await runUnsupervised(family, {
        rows: DEMO_ROWS,
        algorithm,
        n_clusters: 3,
        n_components: 2,
        contamination: 0.1,
        seed: 42,
      });
      setResult(out);
      setStatus("Done");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setStatus("");
    }
  }

  const algos =
    family === "dr"
      ? ["pca", "svd", "tsne"]
      : family === "anomaly"
        ? ["isolation_forest", "lof"]
        : ["kmeans", "agglomerative"];

  return (
    <div className="space-y-6 p-6">
      <header>
        <h1 className="font-display text-2xl text-[var(--ink)]">Unsupervised · {mode}</h1>
        <p className="mt-1 text-sm text-[var(--muted)]">
          Clustering, DR and anomaly via sklearn (seed 42). Demo uses a synthetic 40×3 matrix.
        </p>
      </header>

      <div className="flex flex-wrap items-end gap-3">
        <label className="text-sm">
          Algorithm
          <select
            className="ml-2 border border-[var(--line)] bg-transparent px-2 py-1"
            value={algorithm}
            onChange={(e) => setAlgorithm(e.target.value)}
          >
            {algos.map((a) => (
              <option key={a} value={a}>
                {a}
              </option>
            ))}
          </select>
        </label>
        <button
          type="button"
          className="bg-[var(--gold)] px-3 py-1.5 text-sm text-[var(--ink)]"
          onClick={() => void run()}
        >
          Run
        </button>
      </div>

      {status && <p className="text-sm text-[var(--muted)]">{status}</p>}
      {error && <p className="text-sm text-red-700">{error}</p>}

      {result && (
        <pre className="max-h-[28rem] overflow-auto border border-[var(--line)] bg-[var(--paper)] p-3 text-xs">
          {JSON.stringify(
            {
              id: result.id,
              algorithm: result.algorithm,
              metrics: result.metrics,
              n_clusters: result.n_clusters,
              n_outliers: result.n_outliers,
              explained_variance_ratio: result.explained_variance_ratio,
              n_components: result.n_components,
            },
            null,
            2
          )}
        </pre>
      )}
    </div>
  );
}
