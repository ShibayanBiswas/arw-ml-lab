"use client";

import dynamic from "next/dynamic";
import { ExplainCard } from "@/components/edu/ExplainCard";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

export type ArtefactView = {
  id: string;
  kind: "plot" | "table" | "metric";
  title: string;
  edu_key?: string | null;
  plotly?: Record<string, unknown> | null;
  png_b64?: string | null;
  numbers?: Record<string, unknown>;
  table?: { columns: string[]; rows: Record<string, unknown>[] } | null;
  sampled?: boolean;
};

type Props = { artefact: ArtefactView };

export function ArtefactPanel({ artefact }: Props) {
  return (
    <section className="panel-stable rounded-2xl p-4" data-artefact-id={artefact.id}>
      <header className="mb-3 flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-medium text-[var(--fg)]">{artefact.title}</h3>
          {artefact.sampled ? (
            <span className="rounded border border-[var(--border)] px-1.5 py-0.5 text-[10px] uppercase text-[var(--fg-muted)]">
              sampled
            </span>
          ) : null}
        </div>
        <div className="flex items-center gap-2">
          {artefact.edu_key ? <ExplainCard eduKey={artefact.edu_key} /> : null}
          {artefact.png_b64 ? (
            <a
              className="text-xs text-[var(--gold)] underline"
              download={`${artefact.id}.png`}
              href={`data:image/png;base64,${artefact.png_b64}`}
            >
              PNG
            </a>
          ) : null}
        </div>
      </header>
      {artefact.kind === "plot" && artefact.plotly ? (
        <Plot
          data={(artefact.plotly as { data?: unknown[] }).data as never[]}
          layout={{
            ...((artefact.plotly as { layout?: object }).layout ?? {}),
            autosize: true,
            paper_bgcolor: "transparent",
            plot_bgcolor: "transparent",
            font: { color: "var(--fg)" },
            margin: { t: 40, r: 20, b: 40, l: 40 },
          }}
          config={{ displayModeBar: false, responsive: true }}
          style={{ width: "100%", height: "320px" }}
          useResizeHandler
        />
      ) : null}
      {artefact.kind === "table" && artefact.table ? (
        <div className="max-h-80 overflow-auto">
          <table className="w-full min-w-[28rem] border-collapse text-left text-xs">
            <thead>
              <tr>
                {artefact.table.columns.map((c) => (
                  <th key={c} className="sticky top-0 border-b border-[var(--border)] bg-[var(--bg-elevated)] px-2 py-1">
                    {c}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {artefact.table.rows.slice(0, 100).map((row, i) => (
                <tr key={i} className="border-b border-[var(--border)]/50">
                  {artefact.table!.columns.map((c) => (
                    <td key={c} className="px-2 py-1 font-mono text-[11px]">
                      {formatCell(row[c])}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </section>
  );
}

function formatCell(v: unknown): string {
  if (v == null) return "—";
  if (typeof v === "object") return JSON.stringify(v);
  return String(v);
}
