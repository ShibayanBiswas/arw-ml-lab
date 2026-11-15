"use client";

import Link from "next/link";
import { MODULE_ICONS, familyBadge } from "@/lib/module-icons";
import type { ModuleGroup } from "@/lib/modules";

type Props = { mod: ModuleGroup };

export function ModuleHub({ mod }: Props) {
  const Icon = MODULE_ICONS[mod.icon];
  const pages = mod.nav.filter((n) => n.path);

  return (
    <div className="space-y-5" data-testid="module-hub" data-module={mod.id}>
      <header className="panel-luxe relative overflow-hidden rounded-2xl px-5 py-6 md:px-7">
        <div className="flex flex-wrap items-start gap-4">
          <span className="module-icon flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-[color-mix(in_srgb,var(--gold)_16%,var(--bg-muted))] text-[var(--gold)]">
            <Icon size={22} />
          </span>
          <div className="min-w-0 flex-1">
            <p className="section-kicker section-kicker-alive">{mod.id}</p>
            <h1 className="mt-1 font-[family-name:var(--font-display)] text-3xl tracking-tight md:text-4xl">
              {mod.label}
            </h1>
            <p className="mt-2 max-w-2xl text-sm text-[var(--fg-muted)]">{mod.description}</p>
            <p className="mt-3 text-[10px] tracking-[0.16em] text-[var(--fg-subtle)]">
              {familyBadge(mod.requires)} · {pages.length} submodules
            </p>
          </div>
        </div>
      </header>

      <section>
        <p className="section-kicker mb-3">Submodules</p>
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {pages.map((item, index) => (
            <Link
              key={item.id}
              href={item.path!}
              className="module-tile module-tile-animate rounded-2xl p-4"
              style={{ animationDelay: `${40 + index * 35}ms` }}
            >
              <p className="section-kicker m-0 text-[9px]">{item.id}</p>
              <h2 className="mt-1 font-[family-name:var(--font-display)] text-xl">{item.label}</h2>
              {item.description ? (
                <p className="mt-1 text-sm text-[var(--fg-muted)]">{item.description}</p>
              ) : (
                <p className="mt-1 text-sm text-[var(--fg-muted)]">Open {item.label}</p>
              )}
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
