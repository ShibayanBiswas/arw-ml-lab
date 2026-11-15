"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  confirmIntake,
  getIntake,
  listDatasets,
  patchIntake,
  runIntake,
  getJob,
} from "@/lib/api";

type Proposal = {
  id: string;
  merged: {
    family?: {
      proposed?: string;
      financial?: boolean;
      scores?: Record<string, number>;
      preselected?: boolean;
    };
    time_index?: { column?: string; format?: string; ambiguous_format?: boolean } | null;
    frequency?: { alias?: string; calendar?: string; seasonal_periods?: number[] } | null;
    targets?: Array<{ column?: string; derived?: Record<string, unknown>; confidence?: number }>;
    features?: Array<{ column: string; role: string; encoder?: string; transform?: string }>;
    excluded?: Array<{ column: string; reason_code: string; detail?: string }>;
    leakage_suspects?: Array<{ column: string; rule: string; severity: string }>;
    roles?: Record<string, { role: string; included?: boolean; reasons?: string[]; hard_exclude?: boolean }>;
    questions_for_user?: string[];
    confidence_overall?: number;
    horizon?: { h_default?: number; h_max?: number } | null;
    cv_recommendation?: { scheme?: string; reason?: string } | null;
  };
  status: string;
};

export function IntakeReview() {
  const router = useRouter();
  const params = useSearchParams();
  const versionParam = params.get("version");
  const [datasets, setDatasets] = useState<Array<Record<string, unknown>>>([]);
  const [versionId, setVersionId] = useState(versionParam ?? "");
  const [proposal, setProposal] = useState<Proposal | null>(null);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [dateFormat, setDateFormat] = useState<"dd/mm" | "mm/dd">("dd/mm");

  const scores = proposal?.merged.family?.scores ?? {};

  const refresh = useCallback(async () => {
    setDatasets(await listDatasets());
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  useEffect(() => {
    if (versionParam) setVersionId(versionParam);
  }, [versionParam]);

  async function loadProposal(id: string) {
    setStatus("Loading intake…");
    setError("");
    try {
      let p = await getIntake(id);
      if (!p) {
        const { job_id } = await runIntake(id);
        let job = await getJob(job_id);
        while (job.status === "queued" || job.status === "running") {
          await new Promise((r) => setTimeout(r, 200));
          job = await getJob(job_id);
        }
        if (job.status !== "done") throw new Error(job.status);
        p = await getIntake(id);
      }
      if (!p) throw new Error("intake proposal missing");
      setProposal(p as Proposal);
      setStatus(`Proposal ${p.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setStatus("");
    }
  }

  useEffect(() => {
    if (versionId) void loadProposal(versionId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [versionId]);

  const ambiguousDate = Boolean(proposal?.merged.time_index?.ambiguous_format);

  const roleRows = useMemo(() => {
    const roles = proposal?.merged.roles ?? {};
    return Object.entries(roles).map(([column, r]) => ({ column, ...r }));
  }, [proposal]);

  async function onAccept() {
    if (!proposal) return;
    setError("");
    try {
      if (ambiguousDate) {
        await patchIntake(proposal.id, {
          time_index: {
            ...(proposal.merged.time_index ?? {}),
            format: dateFormat === "dd/mm" ? "%d/%m/%Y" : "%m/%d/%Y",
            ambiguous_format: false,
          },
        });
      }
      const res = await confirmIntake(proposal.id);
      setStatus(`Confirmed → experiment ${res.experiment_id}`);
      router.push("/eda/overview");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }

  async function onReset() {
    if (!versionId) return;
    const { job_id } = await runIntake(versionId);
    let job = await getJob(job_id);
    while (job.status === "queued" || job.status === "running") {
      await new Promise((r) => setTimeout(r, 200));
      job = await getJob(job_id);
    }
    await loadProposal(versionId);
  }

  return (
    <div className="space-y-4">
      <section className="panel-stable panel-luxe animate-rise rounded-2xl p-6">
        <p className="section-kicker">Data</p>
        <h1 className="section-title mt-1">Intake Review</h1>
        <p className="mt-2 text-sm text-[var(--fg-muted)]">
          Rule-based proposal (AI adjudicator in Phase 6). Confirm family, roles and target before EDA.
        </p>
        {status ? <p className="mt-2 text-sm text-[var(--gold)]">{status}</p> : null}
        {error ? <p className="mt-2 text-sm text-red-600">{error}</p> : null}
        <div className="mt-4 flex flex-wrap gap-2">
          <select
            className="rounded border border-[var(--border)] bg-transparent px-3 py-2 text-sm"
            value={versionId}
            onChange={(e) => setVersionId(e.target.value)}
          >
            <option value="">Select dataset version…</option>
            {datasets.map((d) => (
              <option key={String(d.id)} value={String(d.id)}>
                {String(d.name)} ({String(d.id).slice(0, 8)})
              </option>
            ))}
          </select>
          <button type="button" className="btn-gold" onClick={() => versionId && void loadProposal(versionId)}>
            Load
          </button>
        </div>
      </section>

      {proposal ? (
        <>
          <section className="panel-stable rounded-2xl p-6">
            <h2 className="font-display text-lg">Family</h2>
            <p className="text-sm text-[var(--fg-muted)]">
              Proposed: <strong>{proposal.merged.family?.proposed}</strong>
              {proposal.merged.family?.financial ? " · Financial" : ""} · confidence{" "}
              {(proposal.merged.confidence_overall ?? 0).toFixed(2)}
            </p>
            <div className="mt-3 grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
              {Object.entries(scores).map(([k, v]) => (
                <div key={k} className="rounded-lg border border-[var(--border)] p-3">
                  <p className="text-xs uppercase tracking-wide text-[var(--fg-muted)]">{k}</p>
                  <div className="mt-2 h-2 rounded bg-[var(--border)]">
                    <div
                      className="h-2 rounded bg-[var(--gold)]"
                      style={{ width: `${Math.round(Number(v) * 100)}%` }}
                    />
                  </div>
                  <p className="mt-1 font-mono text-sm">{Number(v).toFixed(2)}</p>
                </div>
              ))}
            </div>
            {proposal.merged.time_index ? (
              <p className="mt-3 text-sm">
                Time index: {proposal.merged.time_index.column ?? "(composite)"} ·{" "}
                {proposal.merged.frequency?.alias ?? "—"}
                {proposal.merged.horizon
                  ? ` · h_max ${proposal.merged.horizon.h_max}`
                  : ""}
              </p>
            ) : null}
            {ambiguousDate ? (
              <div className="mt-3 rounded-lg border border-amber-500/40 p-3 text-sm">
                Date format is ambiguous (day and month both ≤ 12). Default India dd/mm.
                <div className="mt-2 flex gap-3">
                  <label className="flex items-center gap-2">
                    <input
                      type="radio"
                      checked={dateFormat === "dd/mm"}
                      onChange={() => setDateFormat("dd/mm")}
                    />
                    dd/mm
                  </label>
                  <label className="flex items-center gap-2">
                    <input
                      type="radio"
                      checked={dateFormat === "mm/dd"}
                      onChange={() => setDateFormat("mm/dd")}
                    />
                    mm/dd
                  </label>
                </div>
              </div>
            ) : null}
          </section>

          <section className="panel-stable rounded-2xl p-6">
            <h2 className="font-display text-lg">Targets</h2>
            <ul className="mt-2 space-y-1 text-sm">
              {(proposal.merged.targets ?? []).slice(0, 6).map((t, i) => (
                <li key={i}>
                  {t.derived
                    ? `derived: ${String((t.derived as { builder?: string }).builder)}`
                    : t.column}{" "}
                  <span className="text-[var(--fg-muted)]">
                    ({(t.confidence ?? 0).toFixed(2)})
                  </span>
                </li>
              ))}
            </ul>
          </section>

          <section className="panel-stable rounded-2xl p-6 overflow-x-auto">
            <h2 className="font-display text-lg">Roles</h2>
            <table className="mt-3 w-full min-w-[640px] text-left text-sm">
              <thead>
                <tr className="border-b border-[var(--border)] text-[var(--fg-muted)]">
                  <th className="py-2 pr-2">Column</th>
                  <th className="py-2 pr-2">Role</th>
                  <th className="py-2 pr-2">Include</th>
                  <th className="py-2">Why</th>
                </tr>
              </thead>
              <tbody>
                {roleRows.map((r) => (
                  <tr key={r.column} className="border-b border-[var(--border)]/60">
                    <td className="py-2 pr-2 font-mono">{r.column}</td>
                    <td className="py-2 pr-2">{r.role}</td>
                    <td className="py-2 pr-2">{r.included === false ? "no" : "yes"}</td>
                    <td className="py-2 text-[var(--fg-muted)]">
                      {(r.reasons ?? []).join("; ")}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>

          {(proposal.merged.leakage_suspects?.length ?? 0) > 0 ? (
            <section className="panel-stable rounded-2xl border border-red-500/30 p-6">
              <h2 className="font-display text-lg text-red-700">Leakage suspects</h2>
              <ul className="mt-2 space-y-1 text-sm">
                {proposal.merged.leakage_suspects!.map((s, i) => (
                  <li key={i}>
                    {s.column} — {s.rule} ({s.severity})
                  </li>
                ))}
              </ul>
            </section>
          ) : null}

          {(proposal.merged.questions_for_user?.length ?? 0) > 0 ? (
            <section className="panel-stable rounded-2xl p-6">
              <h2 className="font-display text-lg">Questions</h2>
              <ul className="mt-2 list-disc pl-5 text-sm">
                {proposal.merged.questions_for_user!.map((q) => (
                  <li key={q}>{q}</li>
                ))}
              </ul>
            </section>
          ) : null}

          <section className="flex flex-wrap gap-3">
            <button type="button" className="btn-gold" onClick={() => void onAccept()}>
              Accept all
            </button>
            <button type="button" className="btn-ghost" onClick={() => void onReset()}>
              Reset to rule-based
            </button>
            <button
              type="button"
              className="btn-ghost"
              onClick={() => router.push(`/data/versions`)}
            >
              Compare with previous version
            </button>
          </section>
        </>
      ) : null}
    </div>
  );
}
