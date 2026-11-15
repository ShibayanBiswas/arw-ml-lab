"use client";

import { useEffect, useState } from "react";
import { Clock } from "lucide-react";

/** Lab terminal chrome — IST clock + integrity pills (no markets tape). */
export function TerminalHeader() {
  const [now, setNow] = useState<Date | null>(null);

  useEffect(() => {
    const tick = () => setNow(new Date());
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);

  const timeStr =
    now?.toLocaleTimeString("en-IN", {
      timeZone: "Asia/Kolkata",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: true,
    }) ?? "--:--:--";

  const dateStr =
    now?.toLocaleDateString("en-IN", {
      timeZone: "Asia/Kolkata",
      weekday: "short",
      day: "numeric",
      month: "short",
    }) ?? "";

  return (
    <div
      className="terminal-header terminal-header-luxe panel-stable panel-luxe flex flex-wrap items-center justify-between gap-3 rounded-xl px-4 py-2.5 md:px-5"
      data-testid="terminal-header"
    >
      <div className="flex flex-wrap items-center gap-3 pl-1">
        <p className="section-kicker section-kicker-alive m-0">Machine Learning Lab</p>
        <span className="status-pill">Seed 42</span>
        <span className="status-pill">No fabricated metrics</span>
      </div>
      <div className="flex items-center gap-2 text-[11px] tracking-[0.08em] text-[var(--fg-muted)]">
        <Clock size={13} className="text-[var(--gold)]" />
        <span className="font-[family-name:var(--font-mono)] tabular-nums">{timeStr}</span>
        <span className="text-[var(--fg-subtle)]">IST</span>
        {dateStr ? <span className="hidden text-[var(--fg-subtle)] sm:inline">· {dateStr}</span> : null}
      </div>
    </div>
  );
}
