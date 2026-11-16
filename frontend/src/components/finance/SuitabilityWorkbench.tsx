"use client";

import { useState } from "react";
import { runSuitability } from "@/lib/api";

export function SuitabilityWorkbench() {
  const [sampleId, setSampleId] = useState("DS30");
  const [status, setStatus] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [report, setReport] = useState<Record<string, unknown> | null>(null);

  async function run() {
    setError(null);
    setStatus("Running FS1–FS5…");
    try {
      const out = await runSuitability({ sample_id: sampleId });
      setReport(out);
      setStatus(String(out.status ?? "done"));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setStatus("");
    }
  }

  const checks = (report?.checks as Array<Record<string, unknown>> | undefined) ?? [];

  return (
    <div className="space-y-6 p-6">
      <header>
        <h1 className="font-display text-2xl text-[var(--ink)]">Label suitability</h1>
        <p className="mt-1 text-sm text-[var(--muted)]">
          FS1–FS5 traffic lights before financial labels (ARCHITECTURE §37). FS6–FS20 deferred
          until TradingLab adapters.
        </p>
      </header>

      <div className="flex flex-wrap items-end gap-3">
        <label className="text-sm">
          Sample
          <select
            className="ml-2 border border-[var(--line)] bg-transparent px-2 py-1"
            value={sampleId}
            onChange={(e) => setSampleId(e.target.value)}
          >
            <option value="DS30">DS30 NIFTY 50 daily</option>
            <option value="DS22">DS22 Airline passengers</option>
          </select>
        </label>
        <button
          type="button"
          className="bg-[var(--gold)] px-3 py-1.5 text-sm text-[var(--ink)]"
          onClick={() => void run()}
        >
          Run suitability
        </button>
      </div>

      {status && <p className="text-sm text-[var(--muted)]">Status: {status}</p>}
      {error && <p className="text-sm text-red-700">{error}</p>}

      {checks.length > 0 && (
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="border-b border-[var(--line)] text-left">
              <th className="py-1 pr-3">Code</th>
              <th className="py-1 pr-3">Status</th>
              <th className="py-1">Message</th>
            </tr>
          </thead>
          <tbody>
            {checks.map((c) => (
              <tr key={String(c.code)} className="border-b border-[var(--line)]/40">
                <td className="py-1 pr-3 font-mono">{String(c.code)}</td>
                <td className="py-1 pr-3">{String(c.status)}</td>
                <td className="py-1 text-[var(--muted)]">{String(c.message)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {Array.isArray(report?.recommendations) &&
        (report.recommendations as string[]).length > 0 && (
          <ul className="list-disc pl-5 text-sm">
            {(report.recommendations as string[]).map((r) => (
              <li key={r}>{r}</li>
            ))}
          </ul>
        )}
    </div>
  );
}
