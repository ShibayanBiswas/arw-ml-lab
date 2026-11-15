"use client";

import { useState, type FormEvent } from "react";
import { createClient } from "@/lib/supabase/client";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    const supabase = createClient();
    const { error: err } = await supabase.auth.signInWithOtp({
      email,
      options: {
        emailRedirectTo: `${window.location.origin}/auth/callback`,
        shouldCreateUser: true,
      },
    });
    setLoading(false);
    if (err) {
      setError(err.message);
      return;
    }
    setSent(true);
  }

  return (
    <main className="flex min-h-dvh items-center justify-center bg-[var(--bg)] px-4">
      <form
        onSubmit={onSubmit}
        className="panel-stable panel-luxe w-full max-w-md rounded-2xl p-8"
        data-testid="login-form"
      >
        <p className="section-kicker">Sign in</p>
        <h1 className="section-title mt-2 text-3xl">
          <span className="gold-text">ARW</span> ML Lab
        </h1>
        <p className="mt-2 text-sm text-[var(--fg-muted)]">
          Email OTP / magic link via Supabase Auth. Local mail: Inbucket at port 54324.
        </p>
        {sent ? (
          <p className="mt-6 text-sm text-[var(--success)]" role="status">
            Check your inbox for the login link (Inbucket locally).
          </p>
        ) : (
          <>
            <label className="mt-6 block text-sm" htmlFor="email">
              Work email
            </label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 w-full rounded-lg border border-[var(--border)] bg-[var(--bg-elevated)] px-3 py-2"
              placeholder="you@rathi.com"
              autoComplete="email"
            />
            {error ? (
              <p className="mt-2 text-sm text-[var(--danger)]" role="alert">
                {error}
              </p>
            ) : null}
            <button
              type="submit"
              disabled={loading}
              className="mt-4 w-full rounded-lg gold-gradient py-2.5 text-sm font-semibold text-[#111]"
            >
              {loading ? "Sending…" : "Send magic link"}
            </button>
          </>
        )}
      </form>
    </main>
  );
}
