"use client";

import { useMemo, useState } from "react";
import katex from "katex";
import "katex/dist/katex.min.css";
import { EDA_EXPLANATIONS } from "@/content/explanations";

const CATEGORY: Record<string, string> = {
  algorithms: "algorithm",
  metrics: "metric",
  plots: "plot.",
  tests: "test.",
  encodings: "enc.",
  cv: "cv.",
  glossary: "",
};

export function LogicAtlas({ page }: { page: string }) {
  const [q, setQ] = useState("");
  const prefix = CATEGORY[page] ?? "";

  const items = useMemo(() => {
    const base = EDA_EXPLANATIONS.filter((e) => {
      if (!prefix) return true;
      if (page === "plots") return e.key.startsWith("plot.") || e.key.includes("eda.p");
      if (page === "tests") return e.key.startsWith("test.") || e.key.includes("normality") || e.key.includes("stationarity");
      if (page === "glossary" || page === "algorithms" || page === "metrics" || page === "encodings" || page === "cv") {
        return true;
      }
      return e.key.includes(prefix);
    });
    const qq = q.trim().toLowerCase();
    if (!qq) return base;
    return base.filter(
      (e) =>
        e.title.toLowerCase().includes(qq) ||
        e.key.toLowerCase().includes(qq) ||
        e.intuitive.toLowerCase().includes(qq)
    );
  }, [page, prefix, q]);

  return (
    <div className="space-y-4">
      <section className="panel-stable panel-luxe animate-rise rounded-2xl p-6">
        <p className="section-kicker">Learn · Logic Atlas</p>
        <h1 className="section-title mt-1 capitalize">{page}</h1>
        <input
          className="mt-4 w-full max-w-xl rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3 py-2 text-sm"
          placeholder="Search explanations…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
      </section>
      <div className="grid gap-3 md:grid-cols-2">
        {items.map((e) => {
          const mathHtml = katex.renderToString(e.math, { throwOnError: false, displayMode: true });
          return (
            <article key={e.key} className="panel-stable rounded-2xl p-4">
              <p className="font-mono text-[10px] text-[var(--fg-muted)]">{e.key}</p>
              <h2 className="mt-1 font-[family-name:var(--font-display)] text-xl">{e.title}</h2>
              <p className="mt-2 text-sm">{e.intuitive}</p>
              <div className="mt-3 overflow-x-auto rounded-lg bg-[var(--bg)] p-2" dangerouslySetInnerHTML={{ __html: mathHtml }} />
            </article>
          );
        })}
      </div>
    </div>
  );
}
