/**
 * In-process user/OTP store (Vercel warm instances + local).
 * Seeded from TEAM_MEMBERS + SEED_DEFAULT_PASSWORD_MAP.
 * Postgres migration exists for hosted durability (service-role sync later).
 */
import { TEAM_MEMBERS, resolveLoginEmail } from "@/data/team";
import { hashPassword, newId, generateOtp } from "@/lib/auth/crypto";

export type AppUser = {
  id: string;
  email: string;
  name: string;
  role: string;
  passwordHash: string;
  activeSessionId: string | null;
};

export type OtpRow = {
  id: string;
  userId: string;
  email: string;
  code: string;
  expiresAt: number;
  consumed: boolean;
};

declare global {
  // eslint-disable-next-line no-var
  var __mlAuthUsers: Map<string, AppUser> | undefined;
  // eslint-disable-next-line no-var
  var __mlAuthOtps: Map<string, OtpRow> | undefined;
}

function users(): Map<string, AppUser> {
  if (!globalThis.__mlAuthUsers) globalThis.__mlAuthUsers = new Map();
  return globalThis.__mlAuthUsers;
}

function otps(): Map<string, OtpRow> {
  if (!globalThis.__mlAuthOtps) globalThis.__mlAuthOtps = new Map();
  return globalThis.__mlAuthOtps;
}

function passwordMap(): Record<string, string> {
  try {
    const raw = process.env.SEED_DEFAULT_PASSWORD_MAP;
    if (raw) return JSON.parse(raw) as Record<string, string>;
  } catch {
    /* ignore */
  }
  // Local/dev default only — override in production via env
  const out: Record<string, string> = {};
  for (const m of TEAM_MEMBERS) {
    out[m.email.toLowerCase()] = "Lab@ChangeMe1";
  }
  return out;
}

export async function ensureSeeded(): Promise<void> {
  const u = users();
  if (u.size > 0) return;
  const pw = passwordMap();
  for (const m of TEAM_MEMBERS) {
    const email = m.email.toLowerCase();
    const id = newId();
    u.set(email, {
      id,
      email,
      name: m.name,
      role: m.role === "admin" ? "admin" : "scientist",
      passwordHash: await hashPassword(pw[email] || "Lab@ChangeMe1"),
      activeSessionId: null,
    });
  }
}

export async function findUserByEmail(email: string): Promise<AppUser | null> {
  await ensureSeeded();
  const canonical = resolveLoginEmail(email);
  return users().get(canonical) ?? null;
}

export async function setActiveSession(userId: string, sid: string | null): Promise<void> {
  for (const u of users().values()) {
    if (u.id === userId) {
      u.activeSessionId = sid;
      return;
    }
  }
}

export async function createOtp(user: AppUser): Promise<{ otp: OtpRow; code: string }> {
  const code = generateOtp();
  const id = newId();
  const row: OtpRow = {
    id,
    userId: user.id,
    email: user.email,
    code,
    expiresAt: Date.now() + 10 * 60 * 1000,
    consumed: false,
  };
  for (const [k, v] of otps()) {
    if (v.userId === user.id && !v.consumed) otps().delete(k);
  }
  otps().set(id, row);
  return { otp: row, code };
}

export async function consumeOtp(otpId: string, code: string): Promise<OtpRow | null> {
  const row = otps().get(otpId);
  if (!row || row.consumed) return null;
  if (row.expiresAt < Date.now()) return null;
  if (row.code !== code) return null;
  row.consumed = true;
  return row;
}

export function isRosterEmail(email: string): boolean {
  const canonical = resolveLoginEmail(email);
  return TEAM_MEMBERS.some((m) => m.email.toLowerCase() === canonical);
}
