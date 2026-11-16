"use client";

import { useEffect, useState } from "react";
import { labApiBase } from "@/lib/api";

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

  useEffect(() => {
    if (mode !== "health" && mode !== "workers") return;
    void fetch(`${labApiBase()}/healthz`)
      .then(async (r) => {
        if (!r.ok) throw new Error(String(r.status));
        setHealth((await r.json()) as Record<string, unknown>);
      })
      .catch((e) => setError(String(e)));
  }, [mode]);

  return (
    <div className="space-y-6 p-6">
      <header>
        <h1 className="font-display text-2xl text-[var(--ink)]">Admin · {mode}</h1>
        <p className="mt-1 text-sm text-[var(--muted)]">
          System health and settings. NVIDIA keys stay on the API host only.
        </p>
      </header>
      {error && (
        <p className="text-sm text-red-700">
          {error}
          <span className="mt-1 block text-[var(--muted)]">
            lab-api may be unreachable until Render is provisioned.
          </span>
        </p>
      )}
      {(mode === "health" || mode === "workers") && health && (
        <pre className="border border-[var(--line)] p-3 text-xs">{JSON.stringify(health, null, 2)}</pre>
      )}
      {mode === "vlm" && (
        <p className="text-sm text-[var(--muted)]">
          Workspace classification gates providers (public / internal / restricted). Numbers-only
          always available. Keys never appear in the browser.
        </p>
      )}
      {mode === "users" && (
        <p className="text-sm text-[var(--muted)]">Supabase Auth roster — managed in hosted project.</p>
      )}
    </div>
  );
}
