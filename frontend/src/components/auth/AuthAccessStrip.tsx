"use client";

import type { ReactNode } from "react";
import { Clock, KeyRound, ShieldCheck } from "lucide-react";

type Variant = "login" | "password";

type Props = {
  variant?: Variant;
};

function Pill({ children }: { children: ReactNode }) {
  return <span className="auth-access-pill">{children}</span>;
}

export function AuthAccessStrip({ variant = "login" }: Props) {
  if (variant === "password") {
    return (
      <div className="auth-access-strip">
        <div className="auth-access-icon auth-access-icon-lg" aria-hidden>
          <ShieldCheck size={22} strokeWidth={1.75} />
        </div>
        <div className="auth-access-body">
          <p className="auth-access-title">Secure password update</p>
          <p className="auth-access-copy">
            Confirm your current password, then choose a new one. Roster emails
            only — nothing is sent by email.
          </p>
          <div className="auth-access-pills">
            <Pill>Current + new</Pill>
            <Pill>Roster emails only</Pill>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-access-strip">
      <div className="auth-access-icon auth-access-icon-lg" aria-hidden>
        <ShieldCheck size={22} strokeWidth={1.75} />
      </div>
      <div className="auth-access-body">
        <p className="auth-access-title">Secure access</p>
        <p className="auth-access-copy">
          Sign in with your Anand Rathi Wealth credentials. Sessions last 12
          hours on this workstation.
        </p>
        <div className="auth-access-pills">
          <Pill>
            <KeyRound size={12} className="inline shrink-0" />
            Credentials
          </Pill>
          <Pill>ML Lab only</Pill>
          <Pill>
            <Clock size={12} className="inline shrink-0" />
            12h session
          </Pill>
        </div>
      </div>
    </div>
  );
}
