import { JobProgress } from "@/components/jobs/JobProgress";
import { MODULES } from "@/lib/modules";

export default function HomeTerminalPage() {
  return (
    <div className="space-y-6">
      <header className="terminal-header-luxe rounded-2xl p-6">
        <p className="section-kicker section-kicker-alive">Home Terminal</p>
        <h1 className="section-title mt-2 text-3xl">Welcome to ARW ML Lab</h1>
        <p className="mt-2 max-w-2xl text-sm text-[var(--fg-muted)]">
          Foundations shell is live. Dataset upload, EDA and modelling arrive in later phases.
          Seed defaults to 42. No fabricated metrics.
        </p>
      </header>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {MODULES.map((mod) => (
          <a
            key={mod.id}
            href={mod.href}
            className="module-tile module-tile-animate rounded-2xl p-4"
          >
            <p className="section-kicker">{mod.id}</p>
            <h2 className="mt-1 font-[family-name:var(--font-display)] text-xl">{mod.label}</h2>
            <p className="mt-1 text-sm text-[var(--fg-muted)]">{mod.description}</p>
          </a>
        ))}
      </div>

      <JobProgress />
    </div>
  );
}
