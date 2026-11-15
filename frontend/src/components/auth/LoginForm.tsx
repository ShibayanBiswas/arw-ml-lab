"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { FormEvent, useMemo, useState, Suspense } from "react";
import { ArrowRight, Eye, EyeOff, ShieldCheck } from "lucide-react";
import { AuthDisclaimerModal } from "@/components/auth/AuthDisclaimerModal";
import { AuthAccessStrip } from "@/components/auth/AuthAccessStrip";
import { AuthShell } from "@/components/auth/AuthShell";

function noticeForReason(reason: string | null): string {
  if (reason === "session_expired") {
    return "Your session ended. Sign in again to continue in the lab.";
  }
  if (reason === "logged_out_elsewhere") {
    return "Signed out — this account is active on another device. Only one lab login is allowed at a time.";
  }
  if (reason === "password_changed") {
    return "Password updated. Sign in with your new password.";
  }
  return "";
}

function LoginFormInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const sessionNotice = useMemo(
    () => noticeForReason(searchParams.get("reason")),
    [searchParams],
  );

  const noticeTitle = (() => {
    const e = error.toLowerCase();
    if (e.includes("password") && !e.includes("database")) return "Wrong password";
    if (e.includes("not provisioned") || e.includes("seed")) return "Account not ready";
    if (e.includes("invalid email")) return "Invalid email ID";
    return "Sign-in failed";
  })();

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.error || "Sign-in failed");
        setLoading(false);
        return;
      }
      setLoading(false);
      router.replace(data.redirect || "/");
      router.refresh();
    } catch {
      setError("Network error. Please try again.");
      setLoading(false);
    }
  }

  return (
    <AuthShell subtitle="SECURE ACCESS" variant="signin">
      <div className="auth-card auth-card-large animate-rise auth-card-alive" data-testid="login-form">
        <div className="auth-card-accent" aria-hidden />

        <header className="auth-header">
          <div className="min-w-0 flex-1">
            <p className="auth-eyebrow">Machine Learning Lab</p>
            <h1 className="auth-title">Welcome back</h1>
            <p className="auth-lead">
              Anand Rathi Wealth internal ML lab. Sign in with your work email
              and password.
            </p>
          </div>
          <div className="auth-icon-badge">
            <ShieldCheck size={24} strokeWidth={1.75} />
          </div>
        </header>

        <div className="auth-divider" />

        <AuthAccessStrip variant="login" />

        {sessionNotice ? (
          <p
            className="mb-4 rounded-xl border border-amber-500/30 bg-amber-500/10 px-3 py-2.5 text-sm text-amber-900 dark:text-amber-200"
            role="status"
          >
            {sessionNotice}
          </p>
        ) : null}

        <form onSubmit={onSubmit} className="auth-form">
          <div className="auth-field">
            <label className="auth-label" htmlFor="login-email">
              User ID / Email
            </label>
            <input
              id="login-email"
              className="input-field auth-input w-full"
              type="email"
              autoComplete="username"
              placeholder="name@rathi.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="auth-field">
            <label className="auth-label" htmlFor="login-password">
              Password
            </label>
            <div className="relative">
              <input
                id="login-password"
                className="input-field auth-input w-full pr-12"
                type={showPassword ? "text" : "password"}
                autoComplete="current-password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <button
                type="button"
                className="absolute right-4 top-1/2 -translate-y-1/2 text-[var(--fg-subtle)] transition hover:text-[var(--gold-deep)] dark:hover:text-[var(--gold)]"
                onClick={() => setShowPassword((s) => !s)}
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          {error ? (
            <p className="auth-error" role="alert">
              {error}
            </p>
          ) : null}

          {error ? (
            <AuthDisclaimerModal
              title={noticeTitle}
              message={
                error.toLowerCase().includes("password")
                  ? "The email ID is valid, but the password does not match our records. Please re-enter your password or use Change password."
                  : error.toLowerCase().includes("invalid email")
                    ? "This lab accepts only approved Anand Rathi Wealth Machine Learning Lab email IDs."
                    : error
              }
              onClose={() => setError("")}
            />
          ) : null}

          <div className="auth-actions auth-actions-row">
            <button
              type="submit"
              className="btn-primary auth-submit w-full sm:w-auto sm:min-w-[220px]"
              disabled={loading}
            >
              {loading ? "Authenticating…" : "Continue"}
              {!loading ? <ArrowRight size={16} /> : null}
            </button>
            <Link
              href="/change-password"
              className="btn-gold-secondary auth-secondary-btn w-full sm:w-auto"
            >
              Change password
            </Link>
          </div>
        </form>

        <footer className="auth-footer">
          <p className="auth-footnote">
            Authorised Anand Rathi Wealth Machine Learning Lab personnel only.
          </p>
        </footer>
      </div>
    </AuthShell>
  );
}

export function LoginForm() {
  return (
    <Suspense
      fallback={
        <AuthShell subtitle="SECURE ACCESS" variant="signin">
          <div className="auth-card auth-card-large animate-rise" />
        </AuthShell>
      }
    >
      <LoginFormInner />
    </Suspense>
  );
}
