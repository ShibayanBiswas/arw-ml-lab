"use client";

import Link from "next/link";
import { MODULE_ICONS, familyBadge } from "@/lib/module-icons";
import { MODULES, MODULE_COUNT } from "@/lib/modules";

export function ModuleGallery() {
  return (
    <section className="space-y-3" data-testid="module-gallery">
      <div className="flex flex-wrap items-end justify-between gap-2 px-0.5">
        <div>
          <p className="section-kicker">Modules</p>
          <h2 className="mt-1 font-[family-name:var(--font-display)] text-2xl tracking-tight">
            Lab surface
          </h2>
        </div>
        <p className="text-[11px] tracking-[0.18em] text-[var(--fg-subtle)]">
          {MODULE_COUNT} entries · workflow order
        </p>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {MODULES.map((mod, index) => {
          const Icon = MODULE_ICONS[mod.icon];
          return (
            <Link
              key={mod.id}
              href={mod.href}
              className="module-tile module-tile-animate group rounded-2xl p-4"
              style={{ animationDelay: `${60 + index * 40}ms` }}
            >
              <div className="flex items-start gap-3">
                <span className="module-icon flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[color-mix(in_srgb,var(--gold)_14%,var(--bg-muted))] text-[var(--gold)]">
                  <Icon size={18} />
                </span>
                <div className="min-w-0 flex-1">
                  <p className="section-kicker m-0 text-[9px]">{mod.id}</p>
                  <h3 className="mt-0.5 font-[family-name:var(--font-display)] text-xl leading-tight">
                    {mod.label}
                  </h3>
                  <p className="mt-1 text-sm text-[var(--fg-muted)]">{mod.description}</p>
                  <p className="mt-2 text-[10px] tracking-[0.14em] text-[var(--fg-subtle)]">
                    {familyBadge(mod.requires)} · {mod.nav.length} pages
                  </p>
                </div>
              </div>
            </Link>
          );
        })}
      </div>
    </section>
  );
}
