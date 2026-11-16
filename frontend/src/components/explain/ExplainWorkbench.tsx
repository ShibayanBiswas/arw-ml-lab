"use client";

import { useEffect, useState } from "react";
import { explainRows, getModelSampleRow, listModels } from "@/lib/api";

type Mode = "home" | "global" | "local" | "interactions" | "financial" | "compare";
type Method = "shap" | "permutation" | "lime" | "dice" | "ale";

export function ExplainWorkbench({ mode }: { mode: Mode }) {
  const [models, setModels] = useState<
    Array<{ id: string; task: string; target: string | null; dataset_id: string }>
  >([]);
  const [modelId, setModelId] = useState("");
  const [method, setMethod] = useState<Method>("shap");
  const [status, setStatus] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    void listModels()
      .then((list) => {
        setModels(list);
        if (list[0]) setModelId(list[0].id);
      })
      .catch((e) => setError(String(e)));
  }, []);

  async function runExplain() {
    if (!modelId) {
      setError("Train a model first (Predict → train DS3)");
      return;
    }
    setError(null);
    setStatus("Explaining…");
    try {
      const sample = await getModelSampleRow(modelId);
      const row = (sample.row ?? sample) as Record<string, unknown>;
      const rows = [row, row, row, row, row];
      const needsY = method === "permutation" || method === "dice";
      let targetValues: unknown[] | undefined;
      if (needsY) {
        const target = models.find((m) => m.id === modelId)?.target;
        targetValues = rows.map((r) => (target && target in r ? r[target] : 0));
      }
      const out = await explainRows(modelId, rows, method, targetValues);
      setResult(out);
      setStatus("Done");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setStatus("");
    }
  }

  return (
    <div className="space-y-6 p-6">
      <header>
        <h1 className="font-display text-2xl text-[var(--ink)]">Explain · {mode}</h1>
        <p className="mt-1 text-sm text-[var(--muted)]">
          TreeSHAP, LIME, DiCE, ALE (PyALE), and sklearn permutation (seed 42).
        </p>
      </header>

      <div className="flex flex-wrap items-end gap-3">
        <label className="text-sm">
          Model
          <select
            className="ml-2 border border-[var(--line)] bg-transparent px-2 py-1"
            value={modelId}
            onChange={(e) => setModelId(e.target.value)}
          >
            {models.length === 0 && <option value="">(none)</option>}
            {models.map((m) => (
              <option key={m.id} value={m.id}>
                {m.dataset_id} · {m.task} · {m.id.slice(0, 8)}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          Method
          <select
            className="ml-2 border border-[var(--line)] bg-transparent px-2 py-1"
            value={method}
            onChange={(e) => setMethod(e.target.value as Method)}
          >
            <option value="shap">TreeSHAP</option>
            <option value="lime">LIME</option>
            <option value="dice">DiCE</option>
            <option value="ale">ALE</option>
            <option value="permutation">Permutation</option>
          </select>
        </label>
        <button
          type="button"
          className="bg-[var(--gold)] px-3 py-1.5 text-sm text-[var(--ink)]"
          onClick={() => void runExplain()}
        >
          Run explain
        </button>
      </div>

      {status && <p className="text-sm text-[var(--muted)]">{status}</p>}
      {error && <p className="text-sm text-red-700">{error}</p>}

      {result && (
        <pre className="max-h-[28rem] overflow-auto border border-[var(--line)] bg-[var(--paper)] p-3 text-xs">
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}
