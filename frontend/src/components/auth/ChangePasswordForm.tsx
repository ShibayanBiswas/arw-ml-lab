"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";
import { ArrowRight, Eye, EyeOff, LockKeyhole } from "lucide-react";
import { AuthAccessStrip } from "@/components/auth/AuthAccessStrip";
import { AuthDisclaimerModal } from "@/components/auth/AuthDisclaimerModal";
import { AuthShell } from "@/components/auth/AuthShell";

function validatePassword(password: string): string | null {
  if (password.length < 8) return "Password must be at least 8 characters.";
  if (!/[A-Z]/.test(password)) return "Password must include an uppercase letter.";
  if (!/[a-z]/.test(password)) return "Password must include a lowercase letter.";
  if (!/[0-9]/.test(password)) return "Password must include a number.";
  return null;
}

export function ChangePasswordForm() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [currentPassword, setCurrentPassword] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);

  useEffect(() => {
    const frame = window.requestAnimationFrame(() => {
      const stored = sessionStorage.getItem("ml_login_email") || "";
      if (stored) setEmail(stored);
    });
    return () => window.cancelAnimationFrame(frame);
  }, []);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    const strength = validatePassword(password);
    if (strength) {
      setError(strength);
      return;
    }
    if (password !== confirm) {
      setError("New passwords do not match.");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch("/api/auth/change-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          email,
          currentPassword,
          newPassword: password,
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.error || "Unable to update password");
        setLoading(false);
        return;
      }
      sessionStorage.setItem("ml_login_email", email);
      setDone(true);
      setLoading(false);
      window.setTimeout(() => {
        router.replace("/login?reason=password_changed");
        router.refresh();
      }, 1200);
    } catch {
      setError("Network error");
      setLoading(false);
    }
  }

  return (
    <AuthShell subtitle="PASSWORD" variant="recover">
      <div className="auth-card auth-card-large animate-rise auth-card-alive" data-testid="change-password-form">
        <div className="auth-card-accent" aria-hidden />

        <header className="auth-header">
          <div className="min-w-0 flex-1">
            <p className="auth-eyebrow">Machine Learning Lab</p>
            <h1 className="auth-title">Change your password</h1>
            <p className="auth-lead">
              Enter your registered email, current password, and a new password.
              Nothing is sent by email.
            </p>
          </div>
          <div className="auth-icon-badge">
            <LockKeyhole size={24} strokeWidth={1.75} />
          </div>
        </header>

        <div className="auth-divider" />

        <AuthAccessStrip variant="password" />

        {done ? (
          <p className="mb-4 rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-3 py-2.5 text-sm" role="status">
            Password updated. Redirecting to sign in…
          </p>
        ) : null}

        <form onSubmit={onSubmit} className="auth-form">
          <div className="auth-field">
            <label className="auth-label" htmlFor="cp-email">
              Registered email
            </label>
            <input
              id="cp-email"
              className="input-field auth-input w-full"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@rathi.com"
              autoComplete="username"
            />
          </div>

          <div className="auth-field">
            <label className="auth-label" htmlFor="cp-current">
              Current password
            </label>
            <input
              id="cp-current"
              className="input-field auth-input w-full"
              type={showPw ? "text" : "password"}
              required
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              autoComplete="current-password"
            />
          </div>

          <div className="auth-field">
            <label className="auth-label" htmlFor="cp-new">
              New password
            </label>
            <div className="relative">
              <input
                id="cp-new"
                className="input-field auth-input w-full pr-12"
                type={showPw ? "text" : "password"}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="new-password"
              />
              <button
                type="button"
                className="absolute right-4 top-1/2 -translate-y-1/2 text-[var(--fg-subtle)]"
                onClick={() => setShowPw((s) => !s)}
                aria-label={showPw ? "Hide password" : "Show password"}
              >
                {showPw ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          <div className="auth-field">
            <label className="auth-label" htmlFor="cp-confirm">
              Confirm new password
            </label>
            <input
              id="cp-confirm"
              className="input-field auth-input w-full"
              type={showPw ? "text" : "password"}
              required
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              autoComplete="new-password"
            />
          </div>

          {error ? <p className="auth-error">{error}</p> : null}

          {error === "Invalid email ID." ? (
            <AuthDisclaimerModal
              title="Invalid email ID"
              message="Password changes are available only for approved Anand Rathi Wealth Machine Learning Lab email IDs."
              onClose={() => setError("")}
            />
          ) : null}

          <div className="auth-actions">
            <button
              type="submit"
              className="btn-primary auth-submit w-full"
              disabled={loading || done}
            >
              {loading ? "Updating…" : "Update password"}
              {!loading ? <ArrowRight size={16} /> : null}
            </button>
          </div>
        </form>

        <footer className="auth-footer">
          <Link href="/login" className="auth-link auth-back">
            ← Back to sign in
          </Link>
        </footer>
      </div>
    </AuthShell>
  );
}
