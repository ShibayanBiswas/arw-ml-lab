export function AuthAccessStrip() {
  return (
    <div className="auth-access-strip mt-4 flex flex-wrap gap-2 text-[10px] font-semibold tracking-[0.18em] text-[var(--fg-subtle)]">
      <span className="rounded-full border border-[var(--border)] px-2 py-1">Local OTP</span>
      <span className="rounded-full border border-[var(--border)] px-2 py-1">On-screen OTP</span>
      <span className="rounded-full border border-[var(--border)] px-2 py-1">Nothing is sent by email</span>
    </div>
  );
}
