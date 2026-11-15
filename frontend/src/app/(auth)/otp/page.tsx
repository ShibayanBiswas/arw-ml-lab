"use client";

import { useEffect, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { AuthShell } from "@/components/auth/AuthShell";

export default function OtpPage() {
  const router = useRouter();
  const [code, setCode] = useState("");
  const [preview, setPreview] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setPreview(sessionStorage.getItem("ml_otp_preview"));
  }, []);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/auth/verify-otp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code }),
      });
      const data = (await res.json()) as { error?: string };
      if (!res.ok) {
        setError(data.error || "Verification failed");
        setLoading(false);
        return;
      }
      sessionStorage.removeItem("ml_otp_preview");
      router.replace("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      setLoading(false);
    }
  }

  return (
    <AuthShell subtitle="VERIFY" variant="verify">
      <form onSubmit={onSubmit} className="auth-card panel-luxe rounded-2xl p-8" data-testid="otp-form">
        <p className="section-kicker">Step 2 of 2</p>
        <h1 className="section-title mt-2 text-3xl">Enter OTP</h1>
        <p className="mt-2 text-sm text-[var(--fg-muted)]">
          Enter the 6-digit code shown below (nothing is emailed).
        </p>
        {preview ? (
          <div className="auth-otp-panel mt-6 rounded-xl border border-[var(--border)] bg-[var(--bg-elevated)] p-4 text-center">
            <p className="text-[10px] font-bold tracking-[0.28em] text-[var(--fg-subtle)]">ON-SCREEN CODE</p>
            <p className="auth-otp-code mt-2 font-[family-name:var(--font-mono)] text-3xl tracking-[0.4em] text-[var(--gold)]">
              {preview}
            </p>
          </div>
        ) : null}
        <label className="mt-6 block text-sm" htmlFor="code">
          Code
        </label>
        <input
          id="code"
          inputMode="numeric"
          pattern="[0-9]{6}"
          maxLength={6}
          required
          value={code}
          onChange={(e) => setCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
          className="mt-1 w-full rounded-lg border border-[var(--border)] bg-[var(--bg-elevated)] px-3 py-2 tracking-[0.3em]"
          autoComplete="one-time-code"
        />
        {error ? (
          <p className="mt-2 text-sm text-[var(--danger)]" role="alert">
            {error}
          </p>
        ) : null}
        <button
          type="submit"
          disabled={loading || code.length !== 6}
          className="mt-4 w-full rounded-lg gold-gradient py-2.5 text-sm font-semibold text-[#111]"
        >
          {loading ? "Verifying…" : "Enter lab"}
        </button>
      </form>
    </AuthShell>
  );
}
