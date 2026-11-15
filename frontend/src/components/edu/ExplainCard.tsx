"use client";

import { useEffect, useId, useState } from "react";
import katex from "katex";
import "katex/dist/katex.min.css";
import { resolveExplanation } from "@/content/explanations";

type Props = {
  eduKey: string;
  compact?: boolean;
};

export function ExplainCard({ eduKey, compact = false }: Props) {
  const [open, setOpen] = useState(false);
  const panelId = useId();
  const exp = resolveExplanation(eduKey);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  if (!exp) {
    return (
      <button
        type="button"
        className="inline-flex h-6 w-6 items-center justify-center rounded-full border border-[var(--border)] text-xs text-[var(--fg-muted)]"
        title={`No explanation for ${eduKey}`}
        aria-label="Explanation unavailable"
      >
        ⓘ
      </button>
    );
  }

  const mathHtml = katex.renderToString(exp.math, { throwOnError: false, displayMode: true });

  return (
    <span className="relative inline-flex">
      <button
        type="button"
        className="inline-flex h-6 w-6 items-center justify-center rounded-full border border-[var(--gold)]/40 text-xs text-[var(--gold)] hover:bg-[var(--gold)]/10"
        aria-expanded={open}
        aria-controls={panelId}
        onClick={() => setOpen((v) => !v)}
        title={exp.title}
      >
        ⓘ
      </button>
      {open ? (
        <div
          id={panelId}
          role="dialog"
          aria-label={exp.title}
          className="absolute right-0 z-40 mt-8 w-[min(28rem,90vw)] rounded-xl border border-[var(--border)] bg-[var(--bg-elevated)] p-4 shadow-xl"
        >
          <div className="flex items-start justify-between gap-3">
            <h3 className="font-[family-name:var(--font-display)] text-lg text-[var(--fg)]">{exp.title}</h3>
            <button type="button" className="text-sm text-[var(--fg-muted)]" onClick={() => setOpen(false)}>
              Close
            </button>
          </div>
          <p className="mt-2 text-sm text-[var(--fg)]">{exp.intuitive}</p>
          {!compact ? <p className="mt-2 text-sm text-[var(--fg-muted)]">{exp.detail}</p> : null}
          <div className="mt-3 overflow-x-auto rounded-lg bg-[var(--bg)] p-3" dangerouslySetInnerHTML={{ __html: mathHtml }} />
          {!compact ? (
            <>
              <p className="mt-3 text-xs uppercase tracking-wide text-[var(--fg-muted)]">When to use</p>
              <p className="text-sm">{exp.when_to_use}</p>
              {exp.pitfalls.length ? (
                <>
                  <p className="mt-2 text-xs uppercase tracking-wide text-[var(--fg-muted)]">Pitfalls</p>
                  <ul className="list-disc pl-5 text-sm">
                    {exp.pitfalls.map((p) => (
                      <li key={p}>{p}</li>
                    ))}
                  </ul>
                </>
              ) : null}
            </>
          ) : null}
        </div>
      ) : null}
    </span>
  );
}
