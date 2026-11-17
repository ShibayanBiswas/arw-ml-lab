"use client";

import { useCallback, useEffect, useState } from "react";
import { downloadAdminAuditExport, fetchAdminAuditLog, type AuditLogRow } from "@/lib/api";

const IST = "Asia/Kolkata";

function formatIst(iso: string): string {
  if (!iso) return "—";
  try {
    return new Intl.DateTimeFormat("en-IN", {
      timeZone: IST,
      dateStyle: "medium",
      timeStyle: "short",
    }).format(new Date(iso));
  } catch {
    return iso;
  }
}

export function AuditLogPanel() {
  const [rows, setRows] = useState<AuditLogRow[]>([]);
  const [meta, setMeta] = useState<{ id: string; source: string; seed: number } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const out = await fetchAdminAuditLog({ limit: 50 });
      setRows(out.rows);
      setMeta({ id: out.id, source: out.source, seed: out.seed });
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <div className="panel-luxe space-y-4 p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="font-mono text-xs text-[var(--muted)]">ENT.T.AUDIT_LOG</p>
          <p className="text-sm text-[var(--muted)]">
            Workspace audit trail (owner/admin). Times shown in IST.
            {meta ? (
              <span className="ml-2 font-mono text-[10px]">
                source={meta.source} · seed={meta.seed}
              </span>
            ) : null}
          </p>
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            className="border border-[var(--line)] px-3 py-1.5 text-sm hover:border-[var(--gold)]"
            onClick={() => void load()}
            disabled={loading}
          >
            Refresh
          </button>
          <button
            type="button"
            className="border border-[var(--gold)] bg-[var(--gold)]/10 px-3 py-1.5 text-sm text-[var(--ink)]"
            disabled={exporting}
            onClick={() => {
              setExporting(true);
              void downloadAdminAuditExport({ limit: 500 })
                .catch((e) => setError(String(e)))
                .finally(() => setExporting(false));
            }}
          >
            {exporting ? "Exporting…" : "Export CSV"}
          </button>
        </div>
      </div>
      {error && (
        <p className="text-sm text-red-700">
          {error}
          <span className="mt-1 block text-[var(--muted)]">
            Requires lab-api and admin role (Bearer). Demo rows load when Postgres is offline.
          </span>
        </p>
      )}
      {loading && !rows.length ? (
        <p className="text-sm text-[var(--muted)]">Loading audit log…</p>
      ) : null}
      <div className="overflow-x-auto">
        <table className="w-full min-w-[640px] border-collapse text-left text-sm">
          <thead>
            <tr className="border-b border-[var(--line)] text-xs uppercase tracking-wide text-[var(--muted)]">
              <th className="py-2 pr-3">Time (IST)</th>
              <th className="py-2 pr-3">Action</th>
              <th className="py-2 pr-3">Entity</th>
              <th className="py-2 pr-3">Detail</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.id} className="border-b border-[var(--line)]/60">
                <td className="py-2 pr-3 font-mono text-xs">{formatIst(row.created_at)}</td>
                <td className="py-2 pr-3">{row.action}</td>
                <td className="py-2 pr-3 font-mono text-xs">
                  {row.entity ?? "—"}
                  {row.entity_id ? ` · ${row.entity_id}` : ""}
                </td>
                <td className="py-2 pr-3 font-mono text-[10px] text-[var(--muted)]">
                  {JSON.stringify(row.detail)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}