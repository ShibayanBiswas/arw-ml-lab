"use client";

import { useMemo, useState } from "react";
import { runMonitoringKsDrift } from "@/lib/api";

/** Synthetic reference/current slices for demo KS drift (seed 42 via backend metadata). */
function demoMatrices(): {
  reference: number[][];
  current: number[][];
  feature_names: string[];
} {
  const reference: number[][] = [];
  const current: number[][] = [];
  for (let i = 0; i < 40; i++) {
    reference.push([Math.sin(i / 5), Math.cos(i / 4), i * 0.02]);
    current.push([
      Math.sin(i / 5) + (i > 25 ? 0.35 : 0),
      Math.cos(i / 4),
      i * 0.02 + (i % 3) * 0.01,
    ]);
  }
  return { reference, current, feature_names: ["x", "y", "z"] };
}

export function MonitoringDriftPanel() {
  const demo = useMemo(() => demoMatrices(), []);
  const [alpha, setAlpha] = useState(0.01);
  const [status, setStatus] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [report, setReport] = useState<Record<string, unknown> | null>(null);

  async function runKs() {
    setError(null);
    setStatus("KS drift (reference vs current)…");
    try {
      const out = await runMonitoringKsDrift({
        reference: demo.reference,
        current: demo.current,
        feature_names: demo.feature_names,
        alpha,
      });
      setReport(out);
      setStatus("Done");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setStatus("");
    }
  }

  const features = (report?.features as Array<Record<string, unknown>> | undefined) ?? [];

  return (
    <section className="space-y-4 rounded border border-[var(--border)] p-4">
      <header>
        <h2 className="font-display text-lg">Feature drift · Kolmogorov–Smirnov</h2>
        <p className="mt-1 text-sm text-[var(--muted)]">
          Per-feature two-sample KS vs training reference. Demo uses a 40×3 synthetic matrix; artefact{" "}
          <span className="font-mono text-xs">MON.T.KS_DRIFT</span> from lab-api.
        </p>
      </header>
      <div className="flex flex-wrap items-end gap-3">
        <label className="text-sm">
          α (drift if p &lt; α)
          <input
            type="number"
            step="0.001"
            min="0.0001"
            max="0.2"
            className="ml-2 w-24 rounded border border-[var(--border)] bg-transparent px-2 py-1"
            value={alpha}
            onChange={(e) => setAlpha(Number(e.target.value))}
          />
        </label>
        <button
          type="button"
          className="rounded bg-[var(--gold)] px-3 py-1.5 text-sm text-black"
          onClick={() => void runKs()}
        >
          Run KS drift
        </button>
      </div>
      {status ? <p className="text-sm text-[var(--muted)]">{status}</p> : null}
      {error ? <p className="text-sm text-red-600">{error}</p> : null}
      {report ? (
        <div>
          <p className="text-sm">
            Drifted features:{" "}
            <strong>{String(report.n_drifted ?? "—")}</strong> / {String(report.n_features ?? "—")} (α=
            {String(report.alpha ?? alpha)})
          </p>
          <table className="mt-2 w-full border-collapse text-sm">
            <thead>
              <tr className="border-b border-[var(--line)] text-left">
                <th className="py-1 pr-2">Feature</th>
                <th className="py-1 pr-2">KS D</th>
                <th className="py-1 pr-2">p-value</th>
                <th className="py-1">Drift?</th>
              </tr>
            </thead>
            <tbody>
              {features.map((row) => (
                <tr key={String(row.feature)} className="border-b border-[var(--line)]">
                  <td className="py-1 pr-2 font-mono text-xs">{String(row.feature)}</td>
                  <td className="py-1 pr-2">
                    {row.status === "ok" ? Number(row.statistic).toFixed(4) : "—"}
                  </td>
                  <td className="py-1 pr-2">
                    {row.status === "ok" ? Number(row.pvalue).toExponential(2) : "—"}
                  </td>
                  <td className="py-1">{row.drift ? "yes" : row.status === "ok" ? "no" : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </section>
  );
}