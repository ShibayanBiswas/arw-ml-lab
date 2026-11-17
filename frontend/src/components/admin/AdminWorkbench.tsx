"use client";

import { useEffect, useState } from "react";
import { AuditLogPanel } from "@/components/admin/AuditLogPanel";
import { labApiBase, proposeDecision, runInsights } from "@/lib/api";

type Mode =
  | "users"
  | "workspaces"
  | "quotas"
  | "workers"
  | "vlm"
  | "audit"
  | "health";

export function AdminWorkbench({ mode }: { mode: Mode }) {
  const [health, setHealth] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [insight, setInsight] = useState<Record<string, unknown> | null>(null);
  const [decision, setDecision] = useState<Record<string, unknown> | null>(null);
  const [vlmBusy, setVlmBusy] = useState(false);

  useEffect(() => {
    if (mode !== "health" && mode !== "workers") return;
    void fetch(`${labApiBase()}/healthz`)
      .then(async (r) => {
        if (!r.ok) throw new Error(String(r.status));
        setHealth((await r.json()) as Record<string, unknown>);
      })
      .catch((e) => setError(String(e)));
  }, [mode]);

  async function onNumbersOnlyProbe() {
    setVlmBusy(true);
    setError(null);
    try {
      const facts = { seed: 42, balanced_accuracy: 0.75, n_train: 100 };
      const [ins, dec] = await Promise.all([
        runInsights({ stage: "admin", facts, prefer_mock: true, workspace_class: "internal" }),
        proposeDecision({ decision_point: "VD1", facts, numbers_only: true }),
      ]);
      setInsight(ins);
      setDecision(dec);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setVlmBusy(false);
    }
  }

  return (
    <div className="space-y-6 p-6">
      <header>
        <h1 className="font-display text-2xl text-[var(--ink)]">Admin · {mode}</h1>
        <p className="mt-1 text-sm text-[var(--muted)]">
          System health and settings. NVIDIA keys stay on the Contabo API host only.
        </p>
      </header>
      {error && (
        <p className="text-sm text-red-700">
          {error}
          <span className="mt-1 block text-[var(--muted)]">
            lab-api may be unreachable until the Contabo VPS is bootstrapped.
          </span>
        </p>
      )}
      {(mode === "health" || mode === "workers") && health && (
        <pre className="border border-[var(--line)] p-3 text-xs">{JSON.stringify(health, null, 2)}</pre>
      )}
      {mode === "vlm" && (
        <div className="space-y-3" data-artefact="AI.NUMBERS.ONLY">
          <p className="text-sm text-[var(--muted)]">
            Workspace classification gates providers (public / internal / restricted). Numbers-only
            always available. Keys never appear in the browser.
          </p>
          <button
            type="button"
            className="rounded-lg gold-gradient px-4 py-2 text-sm font-semibold text-[#111]"
            disabled={vlmBusy}
            onClick={() => void onNumbersOnlyProbe()}
          >
            {vlmBusy ? "Running…" : "Probe numbers-only insight + VD1"}
          </button>
          {insight ? (
            <pre className="overflow-auto border border-[var(--line)] p-3 text-xs">
              {JSON.stringify(insight, null, 2)}
            </pre>
          ) : null}
          {decision ? (
            <pre
              className="overflow-auto border border-[var(--line)] p-3 text-xs"
              data-artefact="VD.NUMBERS.ONLY"
            >
              {JSON.stringify(decision, null, 2)}
            </pre>
          ) : null}
        </div>
      )}
      {mode === "users" && (
        <p className="text-sm text-[var(--muted)]">Supabase Auth roster — managed in hosted project.</p>
      )}
      {mode === "audit" && <AuditLogPanel />}
    </div>
  );
}
