"use client";

import { useEffect, useState } from "react";

type Props = { name: string };

function greetingForHour(hour: number) {
  if (hour < 12) return "Good morning";
  if (hour < 17) return "Good afternoon";
  return "Good evening";
}

export function Greeting({ name }: Props) {
  const [line, setLine] = useState({ greet: "Welcome", weekday: "", dateLine: "" });

  useEffect(() => {
    const now = new Date();
    const istHour = Number(
      now.toLocaleString("en-US", {
        timeZone: "Asia/Kolkata",
        hour: "numeric",
        hour12: false,
      })
    );
    setLine({
      greet: greetingForHour(Number.isFinite(istHour) ? istHour : now.getHours()),
      weekday: now.toLocaleDateString("en-IN", {
        timeZone: "Asia/Kolkata",
        weekday: "long",
      }),
      dateLine: now.toLocaleDateString("en-IN", {
        timeZone: "Asia/Kolkata",
        day: "numeric",
        month: "long",
        year: "numeric",
      }),
    });
  }, []);

  const display = name.trim() || "there";

  return (
    <section
      className="panel-luxe relative overflow-hidden rounded-2xl px-5 py-6 md:px-7 md:py-8"
      data-testid="home-greeting"
    >
      <div
        aria-hidden
        className="pointer-events-none absolute -right-8 -top-10 h-40 w-40 rounded-full bg-[color-mix(in_srgb,var(--gold)_18%,transparent)] blur-3xl"
      />
      <p className="section-kicker section-kicker-alive relative">Home Terminal</p>
      <h1 className="relative mt-2 font-[family-name:var(--font-display)] text-3xl leading-tight tracking-tight md:text-4xl">
        {line.greet},{" "}
        <span className="gold-text gold-text-shimmer">{display}</span>
      </h1>
      <p className="relative mt-3 max-w-2xl border-l-2 border-[color-mix(in_srgb,var(--gold)_55%,transparent)] pl-3 text-sm text-[var(--fg-muted)] md:text-[15px]">
        Tabular ML workstation for Anand Rathi Wealth — registry-driven modules, leakage-safe
        pipelines, and every number from a real run.
        {line.weekday ? (
          <>
            {" "}
            <span className="text-[var(--fg-subtle)]">
              {line.weekday}
              {line.dateLine ? ` · ${line.dateLine}` : ""}
            </span>
          </>
        ) : null}
      </p>
    </section>
  );
}
