"use client";

import { useEffect, useState } from "react";
import { listModels } from "@/lib/api";

type Mode = "home" | "runs" | "compare" | "registry" | "lineage" | "artifacts";

export function ExperimentsWorkbench({ mode }: { mode: Mode }) {
  const [models, setModels] = useState<
    Array<{ id: string; task: string; target: string | null; dataset_id: string }>
  >([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void listModels()
      .then(setModels)
      .catch((e) => setError(String(e)));
  }, []);

  return (
    <div className="space-y-6 p-6">
      <header>
        <h1 className="font-display text-2xl text-[var(--ink)]">Experiments · {mode}</h1>
        <p className="mt-1 text-sm text-[var(--muted)]">
          In-memory model registry (durable MLflow registry in Phase 7-cont). Seed 42.
        </p>
      </header>
      {error && <p className="text-sm text-red-700">{error}</p>}

      <section>
        <h2 className="text-sm font-medium">Registered models ({models.length})</h2>
        <ul className="mt-2 space-y-1 text-sm">
          {models.length === 0 && (
            <li className="text-[var(--muted)]">None yet — train from Predict / Supervised.</li>
          )}
          {models.map((m) => (
            <li key={m.id} className="font-mono">
              {m.id.slice(0, 8)}… · {m.dataset_id} · {m.task}
              {m.target ? ` · ${m.target}` : ""}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
