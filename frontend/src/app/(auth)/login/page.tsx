"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { AuthShell } from "@/components/auth/AuthShell";
import { AuthAccessStrip } from "@/components/auth/AuthAccessStrip";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [showPw, setShowPw] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = (await res.json()) as { error?: string; otp?: string };
      if (!res.ok) {
        setError(data.error || "Sign-in failed");
        setLoading(false);
        return;
      }
      if (data.otp) {
        sessionStorage.setItem("ml_otp_preview", data.otp);
        sessionStorage.setItem("ml_login_email", email);
      }
      router.push("/otp");
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      setLoading(false);
    }
  }

  return (
    <AuthShell subtitle="SECURE ACCESS" variant="signin">
      <form onSubmit={onSubmit} className="auth-card panel-luxe rounded-2xl p-8" data-testid="login-form">
        <p className="section-kicker">Two-step secure access</p>
        <h1 className="section-title mt-2 text-3xl">
          <span className="gold-text">Machine Learning</span> Lab
        </h1>
        <p className="mt-2 text-sm text-[var(--fg-muted)]">
          Authorised Anand Rathi Wealth personnel only. Password then on-screen OTP.
        </p>
        <AuthAccessStrip />
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
          placeholder="name@rathi.com"
          autoComplete="email"
        />
        <label className="mt-4 block text-sm" htmlFor="password">
          Password
        </label>
        <div className="relative mt-1">
          <input
            id="password"
            type={showPw ? "text" : "password"}
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-lg border border-[var(--border)] bg-[var(--bg-elevated)] px-3 py-2 pr-16"
            autoComplete="current-password"
          />
          <button
            type="button"
            className="absolute right-2 top-1/2 -translate-y-1/2 text-xs text-[var(--fg-muted)]"
            onClick={() => setShowPw((v) => !v)}
          >
            {showPw ? "Hide" : "Show"}
          </button>
        </div>
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
          {loading ? "Checking…" : "Continue"}
        </button>
      </form>
    </AuthShell>
  );
}
