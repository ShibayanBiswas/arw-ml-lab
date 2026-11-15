"use client";

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
  return (
    <aside className="panel-stable flex h-full flex-col rounded-2xl p-4">
      <p className="section-kicker">AI Insights</p>
      <h2 className="section-title mt-1 text-xl">Rule insights</h2>
      <p className="mt-1 text-xs text-[var(--fg-muted)]">
        Deterministic EDA alerts until Phase 6 hosts the VLM.
      </p>
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
