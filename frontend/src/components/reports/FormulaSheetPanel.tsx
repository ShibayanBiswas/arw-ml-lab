"use client";

import { useMemo, useState } from "react";
import katex from "katex";
import "katex/dist/katex.min.css";
import { runReportsFormulas } from "@/lib/api";

type FormulaEntry = {
  id: string;
  title: string;
  family: string;
  latex: string;
  library: string;
};

export function FormulaSheetPanel() {
  const [status, setStatus] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [entries, setEntries] = useState<FormulaEntry[]>([]);
  const [saved, setSaved] = useState<string | null>(null);
  const [family, setFamily] = useState<"all" | "classification" | "regression">("all");

  const rendered = useMemo(
    () =>
      entries.map((e) => ({
        ...e,
        html: katex.renderToString(e.latex, { throwOnError: false, displayMode: true }),
      })),
    [entries],
  );

  async function exportSheet(downloadHtml: boolean) {
    setError(null);
    setSaved(null);
    setStatus("Building…");
    try {
      const families =
        family === "all" ? undefined : ([family] as ("classification" | "regression")[]);
      const res = await runReportsFormulas({
        title: "ARW ML Lab formula sheet",
        families,
      });
      setEntries(res.entries as FormulaEntry[]);
      setStatus(`Artefact ${res.id} · seed ${res.seed} · ${res.numbers.count} entries`);
      if (downloadHtml) {
        const blob = new Blob([res.html], { type: "text/html;charset=utf-8" });
        const name = "metric-formula-sheet.html";
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = name;
        a.click();
        URL.revokeObjectURL(url);
        setSaved(name);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setStatus("");
    }
  }

  return (
    <section className="panel-luxe space-y-3 border border-[var(--line)] p-4">
      <h2 className="font-display text-lg text-[var(--ink)]">Formula sheet</h2>
      <p className="text-sm text-[var(--muted)]">
        KaTeX reference export via <span className="font-mono text-xs">REP.T.FORMULAS</span>{" "}
        (ARCHITECTURE §41.4 / §42). No metric values are computed in this artefact.
      </p>
      <div className="flex flex-wrap items-center gap-2">
        <label className="text-sm text-[var(--muted)]" htmlFor="formula-family">
          Family
        </label>
        <select
          id="formula-family"
          className="border border-[var(--line)] bg-transparent px-2 py-1 text-sm"
          value={family}
          onChange={(e) => setFamily(e.target.value as typeof family)}
        >
          <option value="all">All</option>
          <option value="classification">Classification</option>
          <option value="regression">Regression</option>
        </select>
        <button
          type="button"
          className="bg-[var(--gold)] px-3 py-1.5 text-sm text-[var(--ink)]"
          onClick={() => void exportSheet(false)}
        >
          Preview formulas
        </button>
        <button
          type="button"
          className="border border-[var(--line)] px-3 py-1.5 text-sm text-[var(--ink)]"
          onClick={() => void exportSheet(true)}
        >
          Download HTML
        </button>
      </div>
      {status && <p className="text-sm text-[var(--muted)]">{status}</p>}
      {saved && <p className="font-mono text-xs text-[var(--muted)]">{saved}</p>}
      {error && <p className="text-sm text-red-700">{error}</p>}
      {rendered.length > 0 && (
        <ul className="mt-2 max-h-80 space-y-3 overflow-y-auto border-t border-[var(--line)] pt-3">
          {rendered.map((e) => (
            <li key={e.id} className="rounded border border-[var(--line)] p-3">
              <p className="font-mono text-xs text-[var(--muted)]">
                {e.id} · {e.family}
              </p>
              <p className="text-sm font-medium text-[var(--ink)]">{e.title}</p>
              <div
                className="mt-2 overflow-x-auto rounded bg-[var(--bg)] p-2"
                dangerouslySetInnerHTML={{ __html: e.html }}
              />
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}