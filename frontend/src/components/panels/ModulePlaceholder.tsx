type Props = {
  title: string;
  description?: string;
  state?: "empty" | "loading" | "error";
};

export function ModulePlaceholder({
  title,
  description,
  state = "empty",
}: Props) {
  return (
    <section className="panel-stable panel-luxe animate-rise rounded-2xl p-6" data-state={state}>
      <p className="section-kicker">Module</p>
      <h1 className="section-title mt-1">{title}</h1>
      {state === "loading" ? (
        <p className="mt-3 text-sm text-[var(--fg-muted)]">Loading…</p>
      ) : null}
      {state === "error" ? (
        <p className="mt-3 text-sm text-[var(--danger)]">Something went wrong. Retry later.</p>
      ) : null}
      {state === "empty" ? (
        <p className="mt-3 text-sm text-[var(--fg-muted)]">
          {description ?? "This workbench arrives in a later phase. No placeholder metrics."}
        </p>
      ) : null}
    </section>
  );
}
