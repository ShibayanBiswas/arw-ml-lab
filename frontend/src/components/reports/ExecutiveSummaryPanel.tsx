"use client";

import { useState } from "react";
import { runReportsExecutive } from "@/lib/api";

const DEMO_FACTS = {
  seed: 42,
  cv_scheme: "stratified_kfold",
  n_models: 1,
  note: "demo FACTS only — metrics must come from a real run",
};

export function ExecutiveSummaryPanel() {
  const [status, setStatus] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState<string[]>([]);

  async function exportSummary(includePdf: boolean) {
    setError(null);
    setSaved([]);
    setStatus("Exporting…");
    try {
      const res = await runReportsExecutive(
        {
          title: "Demo supervised report",
          stage: "supervised",
          facts: DEMO_FACTS,
        },
        includePdf,
      );
      const htmlBlob = new Blob([res.html], { type: "text/html;charset=utf-8" });
      const htmlName = "demo-executive-summary.html";
      const htmlUrl = URL.createObjectURL(htmlBlob);
      const aHtml = document.createElement("a");
      aHtml.href = htmlUrl;
      aHtml.download = htmlName;
      aHtml.click();
      URL.revokeObjectURL(htmlUrl);
      const names = [htmlName];
      if (includePdf && res.pdf_available && res.pdf_base64) {
        const bin = Uint8Array.from(atob(res.pdf_base64), (c) => c.charCodeAt(0));
        const pdfBlob = new Blob([bin], { type: "application/pdf" });
        const pdfName = "demo-executive-summary.pdf";
        const pdfUrl = URL.createObjectURL(pdfBlob);
        const aPdf = document.createElement("a");
        aPdf.href = pdfUrl;
        aPdf.download = pdfName;
        aPdf.click();
        URL.revokeObjectURL(pdfUrl);
        names.push(pdfName);
      } else if (includePdf && !res.pdf_available) {
        names.push("(PDF skipped — WeasyPrint/Pango not available here)");
      }
      setSaved(names);
      setStatus(`Downloaded (artefact ${res.id}, seed ${res.seed})`);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setStatus("");
    }
  }

  return (
    <section className="panel-luxe space-y-3 border border-[var(--line)] p-4">
      <h2 className="font-display text-lg text-[var(--ink)]">Executive summary</h2>
      <p className="text-sm text-[var(--muted)]">
        HTML (and optional PDF) via <span className="font-mono text-xs">REP.T.EXECUTIVE</span>{" "}
        (ARCHITECTURE §25). FACTS are rendered verbatim; PDF needs WeasyPrint in the API image.
      </p>
      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          className="bg-[var(--gold)] px-3 py-1.5 text-sm text-[var(--ink)]"
          onClick={() => void exportSummary(false)}
        >
          Export demo HTML
        </button>
        <button
          type="button"
          className="border border-[var(--line)] px-3 py-1.5 text-sm text-[var(--ink)]"
          onClick={() => void exportSummary(true)}
        >
          Export HTML + try PDF
        </button>
      </div>
      {status && <p className="text-sm text-[var(--muted)]">{status}</p>}
      {saved.length > 0 && (
        <ul className="font-mono text-xs text-[var(--muted)]">
          {saved.map((n) => (
            <li key={n}>{n}</li>
          ))}
        </ul>
      )}
      {error && <p className="text-sm text-red-700">{error}</p>}
    </section>
  );
}