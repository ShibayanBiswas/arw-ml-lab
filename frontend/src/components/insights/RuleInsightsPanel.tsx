"use client";

import { useState } from "react";
import { runInsights } from "@/lib/api";

export type RuleInsightView = {
  rule_id: string;
  severity: "info" | "warning" | "critical";
  message: string;
  column?: string | null;
  value?: number | null;
};

type Props = {
  insights: RuleInsightView[];
};

const SEV: Record<string, string> = {
  info: "text-[var(--fg-muted)]",
  warning: "text-amber-600",
  critical: "text-red-600",
};

export function RuleInsightsPanel({ insights }: Props) {
  const [ai, setAi] = useState<Record<string, unknown> | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function onNumbersOnly() {
    setBusy(true);
    setErr(null);
    try {
      const facts: Record<string, unknown> = {
        seed: 42,
        n_rule_insights: insights.length,
      };
      for (const ins of insights.slice(0, 12)) {
        if (ins.value != null && Number.isFinite(ins.value)) {
          facts[`rule.${ins.rule_id}${ins.column ? `.${ins.column}` : ""}`] = ins.value;
        }
      }
      const out = await runInsights({
        stage: "eda",
        facts,
        prefer_mock: true,
        workspace_class: "internal",
      });
      setAi(out);
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <aside className="panel-stable flex h-full flex-col rounded-2xl p-4" data-artefact="AI.NUMBERS.ONLY">
      <p className="section-kicker">AI Insights</p>
      <h2 className="section-title mt-1 text-xl">Rule insights</h2>
      <p className="mt-1 text-xs text-[var(--fg-muted)]">
        Deterministic EDA alerts; numbers-only AI cites FACTS when the provider is off.
      </p>
      <button
        type="button"
        className="mt-3 rounded-lg border border-[var(--border)] px-3 py-1.5 text-xs font-medium"
        disabled={busy}
        onClick={() => void onNumbersOnly()}
      >
        {busy ? "Generating…" : "Numbers-only insight"}
      </button>
      {err ? <p className="mt-2 text-xs text-red-700">{err}</p> : null}
      {ai ? (
        <pre className="mt-2 max-h-40 overflow-auto rounded border border-[var(--border)] p-2 text-[10px]">
          {JSON.stringify(ai, null, 2)}
        </pre>
      ) : null}
      <ul className="mt-4 flex-1 space-y-2 overflow-auto">
        {insights.length === 0 ? (
          <li className="text-sm text-[var(--fg-muted)]">No rule alerts for this run.</li>
        ) : (
          insights.map((ins, i) => (
            <li
              key={`${ins.rule_id}-${ins.column ?? i}`}
              className="rounded-lg border border-[var(--border)] px-3 py-2 text-sm"
            >
              <div className="flex items-center justify-between gap-2">
                <span className={`text-[10px] uppercase tracking-wide ${SEV[ins.severity]}`}>
                  {ins.severity}
                </span>
                <span className="font-mono text-[10px] text-[var(--fg-muted)]">{ins.rule_id}</span>
              </div>
              <p className="mt-1 text-[var(--fg)]">{ins.message}</p>
            </li>
          ))
        )}
      </ul>
    </aside>
  );
}
