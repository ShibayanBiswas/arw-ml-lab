"use client";

import { useState } from "react";
import { labApiBase } from "@/lib/api";
import { labAuthHeaders } from "@/lib/lab-session";

type Mode = "home" | "lab" | "sequential";

export function DeepWorkbench({ mode }: { mode: Mode }) {
  const [status, setStatus] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);

  async function runSmoke() {
    setError(null);
    setStatus("Running LSTM sequential smoke…");
    try {
      const res = await fetch(`${labApiBase()}/api/v1/deep/sequential/smoke`, {
        method: "POST",
        headers: { ...labAuthHeaders(), "Content-Type": "application/json" },
        body: JSON.stringify({ model: "lstm", max_epochs: 1, seed: 42 }),
      });
      if (!res.ok) {
        // fallback message if endpoint not yet on this worker image
        const detail = await res.text();
        throw new Error(`${res.status} ${detail}`);
      }
      setResult((await res.json()) as Record<string, unknown>);
      setStatus("Done");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setStatus("");
    }
  }

  return (
    <div className="space-y-6 p-6">
      <header>
        <h1 className="font-display text-2xl text-[var(--ink)]">Deep Learning · {mode}</h1>
        <p className="mt-1 text-sm text-[var(--muted)]">
          Sequential LSTM/TCN with leakage-safe scalers inside purged train windows (seed 42).
        </p>
      </header>
      <button
        type="button"
        className="bg-[var(--gold)] px-3 py-1.5 text-sm text-[var(--ink)]"
        onClick={() => void runSmoke()}
      >
        Run sequential smoke
      </button>
      {status && <p className="text-sm text-[var(--muted)]">{status}</p>}
      {error && (
        <p className="text-sm text-red-700">
          {error}
          <span className="mt-1 block text-[var(--muted)]">
            If 404, the deep router is still wiring — labcore.deep.fit_sequential is available in
            tests.
          </span>
        </p>
      )}
      {result && (
        <pre className="max-h-96 overflow-auto border border-[var(--line)] p-3 text-xs">
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}
