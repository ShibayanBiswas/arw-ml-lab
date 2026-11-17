"use client";

import { useMemo, useState } from "react";
import { ArtefactPanel, type ArtefactView } from "@/components/eda/ArtefactPanel";
import {
  runSuitability,
  runSuitabilityPlot,
  type SuitabilityCataloguePlot,
  type SuitabilityPlotBody,
} from "@/lib/api";

const FS_PLOTS: { id: SuitabilityCataloguePlot; label: string; artefact: string }[] = [
  { id: "volatility", label: "Daily vol (EWMA)", artefact: "FS.P.VOL" },
  { id: "price", label: "Price + CUSUM", artefact: "FS.P.PRICE" },
  { id: "barriers", label: "Sample barriers", artefact: "FS.P.BARRIERS" },
  { id: "uniqueness", label: "Uniqueness / conc.", artefact: "FS.P.UNIQUENESS" },
  { id: "holding", label: "Holding period", artefact: "FS.P.HOLDING" },
  { id: "min-ffd", label: "Min FFD (ADF)", artefact: "FS.P.MIN_FFD" },
  { id: "sadf", label: "SADF", artefact: "FS.P.SADF" },
  { id: "trendscan", label: "Trend scan", artefact: "FS.P.TRENDSCAN" },
  { id: "label-balance", label: "Label balance", artefact: "FS.P.LABEL_BALANCE" },
  { id: "grid", label: "Param grid", artefact: "FS.P.GRID" },
];

export function SuitabilityWorkbench() {
  const [sampleId, setSampleId] = useState("DS30");
  const [status, setStatus] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [report, setReport] = useState<Record<string, unknown> | null>(null);
  const [plotArtefact, setPlotArtefact] = useState<ArtefactView | null>(null);

  const runBody = useMemo(
    (): SuitabilityPlotBody => ({
      sample_id: sampleId,
      horizon: 5,
      vol_span: 100,
      pt_mult: 1.0,
      sl_mult: 1.0,
      n_samples: 3,
      cusum_mult: 1.0,
      label_method: "triple_barrier",
    }),
    [sampleId]
  );

  async function run() {
    setError(null);
    setPlotArtefact(null);
    setStatus("Running FS1–FS5…");
    try {
      const out = await runSuitability(runBody);
      setReport(out);
      setStatus(String(out.status ?? "done"));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setStatus("");
    }
  }

  async function runPlot(plot: SuitabilityCataloguePlot) {
    setError(null);
    setStatus(`Plot ${plot} (${sampleId})…`);
    try {
      const out = await runSuitabilityPlot(plot, runBody);
      const id = String(out.id ?? "");
      setPlotArtefact({
        id,
        kind: "plot",
        title: id || plot,
        plotly: (out.plotly as Record<string, unknown> | undefined) ?? null,
        numbers: (out.numbers as Record<string, unknown> | undefined) ?? undefined,
      });
      setReport({ id: out.id, numbers: out.numbers });
      setStatus("Plot ready");
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
          FS1–FS5 traffic lights plus FS.P.* catalogue plots (DS30 / DS22, seed 42 on lab-api).
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
        {FS_PLOTS.map((p) => (
          <button
            key={p.id}
            type="button"
            className="border border-[var(--line)] px-3 py-1.5 text-sm"
            title={p.artefact}
            onClick={() => void runPlot(p.id)}
          >
            {p.label}
          </button>
        ))}
      </div>

      {status && <p className="text-sm text-[var(--muted)]">Status: {status}</p>}
      {error && <p className="text-sm text-red-700">{error}</p>}

      {plotArtefact ? <ArtefactPanel artefact={plotArtefact} /> : null}

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

      {report && !checks.length && report.numbers ? (
        <pre className="max-h-[28rem] overflow-auto border border-[var(--line)] bg-[var(--paper)] p-3 text-xs">
          {JSON.stringify({ id: report.id, numbers: report.numbers }, null, 2)}
        </pre>
      ) : null}
    </div>
  );
}