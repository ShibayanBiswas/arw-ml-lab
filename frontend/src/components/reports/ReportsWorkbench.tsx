"use client";

import { useState } from "react";
import { labApiBase } from "@/lib/api";
import { labAuthHeaders } from "@/lib/lab-session";
import { ExecutiveSummaryPanel } from "@/components/reports/ExecutiveSummaryPanel";
import { FormulaSheetPanel } from "@/components/reports/FormulaSheetPanel";
import { ReproductionBundlePanel } from "@/components/reports/ReproductionBundlePanel";
import { ReproductionNotebookPanel } from "@/components/reports/ReproductionNotebookPanel";

type Mode = "home" | "builder" | "templates" | "history";

export function ReportsWorkbench({ mode }: { mode: Mode }) {
  const [status, setStatus] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [report, setReport] = useState<Record<string, unknown> | null>(null);

  async function build() {
    setError(null);
    setStatus("Building…");
    try {
      const res = await fetch(`${labApiBase()}/api/v1/reports/build`, {
        method: "POST",
        headers: { ...labAuthHeaders(), "Content-Type": "application/json" },
        body: JSON.stringify({
          title: "Demo supervised report",
          stage: "supervised",
          facts: { seed: 42, n_models: 1, cv_scheme: "stratified_kfold" },
        }),
      });
      if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
      setReport((await res.json()) as Record<string, unknown>);
      setStatus("Done");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setStatus("");
    }
  }

  return (
    <div className="space-y-6 p-6">
      <header>
        <h1 className="font-display text-2xl text-[var(--ink)]">Reports · {mode}</h1>
        <p className="mt-1 text-sm text-[var(--muted)]">
          FACTS-only report builder (ARCHITECTURE §25). AI text is advisory.
        </p>
      </header>
      {mode === "templates" && (
        <>
          <ExecutiveSummaryPanel />
          <FormulaSheetPanel />
          <ReproductionNotebookPanel />
          <ReproductionBundlePanel />
        </>
      )}
      {mode === "builder" && (
        <>
          <button
            type="button"
            className="bg-[var(--gold)] px-3 py-1.5 text-sm text-[var(--ink)]"
            onClick={() => void build()}
          >
            Build demo report
          </button>
          {status && <p className="text-sm text-[var(--muted)]">{status}</p>}
          {error && <p className="text-sm text-red-700">{error}</p>}
          {report && (
            <pre className="max-h-96 overflow-auto border border-[var(--line)] p-3 text-xs">
              {JSON.stringify(report, null, 2)}
            </pre>
          )}
        </>
      )}
      {mode !== "builder" && mode !== "templates" && (
        <p className="text-sm text-[var(--muted)]">Use Builder or Templates for exports.</p>
      )}
    </div>
  );
}