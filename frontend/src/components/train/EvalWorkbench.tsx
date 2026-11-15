"use client";

import { useMemo, useState } from "react";
import { ArtefactPanel, type ArtefactView } from "@/components/eda/ArtefactPanel";

type EvalPayload = {
  classification?: {
    cm?: {
      counts?: number[][];
      norm_true?: number[][];
      labels?: string[];
      derived?: Array<Record<string, unknown>>;
    };
    report?: { rows?: Array<Record<string, unknown>>; footer?: Record<string, unknown> };
    metrics?: Record<string, number>;
    cv_metrics?: { metrics?: Record<string, { mean?: number; std?: number }> };
    threshold?: { methods?: Record<string, { t_star?: number }>; chosen?: { t_star?: number } };
    plots?: ArtefactView[];
    compare?: Record<string, unknown>;
  };
  regression?: {
    resid_tests?: { tests?: Array<{ test: string; statistic?: number; pvalue?: number; verdict?: string }> };
    metrics?: Record<string, number>;
    influence?: { cooks_d_max?: number };
    plots?: ArtefactView[];
  };
};

type Props = {
  evalPayload: EvalPayload | null;
  championKey?: string | null;
};

const TABS = ["Overview", "Confusion", "Report", "Curves", "Residuals"] as const;

export function EvalWorkbench({ evalPayload, championKey }: Props) {
  const [tab, setTab] = useState<(typeof TABS)[number]>("Overview");
  const clf = evalPayload?.classification;
  const ree = evalPayload?.regression;

  const curvePlots = useMemo(
    () => (clf?.plots || []).filter((p) => ["CLE.P.ROC", "CLE.P.PR", "CLE.P.RELIABILITY"].includes(p.id)),
    [clf],
  );
  const cmPlots = useMemo(
    () => (clf?.plots || []).filter((p) => String(p.id).startsWith("CLE.P.CM")),
    [clf],
  );
  const residPlots = useMemo(() => ree?.plots || [], [ree]);

  if (!evalPayload) {
    return (
      <p className="text-sm text-[var(--fg-muted)]">
        Run Quick train to populate §41/§42 evaluation artefacts for the champion model.
      </p>
    );
  }

  return (
    <div className="space-y-4">
      <div>
        <p className="section-kicker">Evaluation</p>
        <h2 className="section-title mt-1 text-2xl">§41 / §42 Eval Core</h2>
        <p className="mt-1 text-sm text-[var(--fg-muted)]">
          Champion: {championKey || "—"} · prediction source OOF (+ hold-out test metrics)
        </p>
      </div>
      <div className="flex flex-wrap gap-2">
        {TABS.map((t) => (
          <button
            key={t}
            type="button"
            className={`rounded-lg px-3 py-1.5 text-sm ${
              tab === t ? "gold-gradient font-semibold text-[#111]" : "border border-[var(--border)]"
            }`}
            onClick={() => setTab(t)}
          >
            {t}
          </button>
        ))}
      </div>

      {tab === "Overview" && (
        <div className="panel-luxe space-y-3 rounded-2xl p-4 text-sm">
          {clf?.metrics && (
            <div>
              <p className="font-semibold">Classification (pooled OOF)</p>
              <ul className="mt-1 grid gap-1 sm:grid-cols-2">
                {Object.entries(clf.metrics)
                  .slice(0, 12)
                  .map(([k, v]) => (
                    <li key={k}>
                      {k}: {Number.isFinite(v) ? v.toFixed(4) : "—"}
                    </li>
                  ))}
              </ul>
              {clf.threshold?.chosen?.t_star != null && (
                <p className="mt-2">Chosen threshold t*: {clf.threshold.chosen.t_star.toFixed(3)}</p>
              )}
            </div>
          )}
          {ree?.metrics && (
            <div>
              <p className="font-semibold">Regression (pooled OOF)</p>
              <ul className="mt-1 grid gap-1 sm:grid-cols-2">
                {Object.entries(ree.metrics).map(([k, v]) => (
                  <li key={k}>
                    {k}: {Number.isFinite(v) ? v.toFixed(4) : "—"}
                  </li>
                ))}
              </ul>
              {ree.influence?.cooks_d_max != null && (
                <p className="mt-2">max Cook&apos;s D: {ree.influence.cooks_d_max.toFixed(4)}</p>
              )}
            </div>
          )}
        </div>
      )}

      {tab === "Confusion" && (
        <div className="space-y-4">
          {cmPlots.length ? cmPlots.map((p) => <ArtefactPanel key={p.id + (p as { title?: string }).title} artefact={p} />) : (
            <p className="text-sm text-[var(--fg-muted)]">No confusion artefacts (regression run).</p>
          )}
        </div>
      )}

      {tab === "Report" && (
        <div className="panel-luxe overflow-x-auto rounded-2xl p-4">
          {clf?.report?.rows ? (
            <table className="min-w-full text-left text-sm">
              <thead>
                <tr>
                  <th className="p-2">class</th>
                  <th className="p-2">precision</th>
                  <th className="p-2">recall</th>
                  <th className="p-2">f1</th>
                  <th className="p-2">support</th>
                </tr>
              </thead>
              <tbody>
                {clf.report.rows.map((r) => (
                  <tr key={String(r.class)} className="border-t border-[var(--border)]">
                    <td className="p-2">{String(r.class)}</td>
                    <td className="p-2">{fmt(r.precision)}</td>
                    <td className="p-2">{fmt(r.recall)}</td>
                    <td className="p-2">{fmt(r.f1)}</td>
                    <td className="p-2">{String(r.support)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="text-sm text-[var(--fg-muted)]">No classification report.</p>
          )}
        </div>
      )}

      {tab === "Curves" && (
        <div className="space-y-4">
          {curvePlots.length ? curvePlots.map((p) => <ArtefactPanel key={p.id} artefact={p} />) : (
            <p className="text-sm text-[var(--fg-muted)]">Curves available for binary classification with probabilities.</p>
          )}
        </div>
      )}

      {tab === "Residuals" && (
        <div className="space-y-4">
          {ree?.resid_tests?.tests && (
            <div className="panel-luxe overflow-x-auto rounded-2xl p-4">
              <table className="min-w-full text-left text-sm">
                <thead>
                  <tr>
                    <th className="p-2">test</th>
                    <th className="p-2">statistic</th>
                    <th className="p-2">p-value</th>
                    <th className="p-2">verdict</th>
                  </tr>
                </thead>
                <tbody>
                  {ree.resid_tests.tests.map((t) => (
                    <tr key={t.test} className="border-t border-[var(--border)]">
                      <td className="p-2">{t.test}</td>
                      <td className="p-2">{t.statistic == null ? "—" : t.statistic.toFixed(4)}</td>
                      <td className="p-2">{t.pvalue == null ? "—" : t.pvalue.toFixed(4)}</td>
                      <td className="p-2">{t.verdict}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {residPlots.map((p) => (
            <ArtefactPanel key={p.id} artefact={p} />
          ))}
          {!ree && <p className="text-sm text-[var(--fg-muted)]">No residual artefacts (classification run).</p>}
        </div>
      )}
    </div>
  );
}

function fmt(v: unknown): string {
  if (typeof v !== "number" || !Number.isFinite(v)) return "—";
  return v.toFixed(4);
}
