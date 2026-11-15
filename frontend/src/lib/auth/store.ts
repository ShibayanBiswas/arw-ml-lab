/**
 * Auth user store — durable via lab_app_users when SUPABASE_SERVICE_ROLE_KEY is set;
 * otherwise in-process Map (local/dev). Seeded from TEAM_MEMBERS + SEED_DEFAULT_PASSWORD_MAP.
 */
import { TEAM_MEMBERS, resolveLoginEmail } from "@/data/team";
import { hashPassword, newId } from "@/lib/auth/crypto";
import {
  authDbEnabled,
  dbFindUserByEmail,
  dbSetActiveSession,
  dbUpdatePassword,
  dbUpsertUser,
  type DbUserRow,
} from "@/lib/auth/db";

export type AppUser = {
  id: string;
  email: string;
  name: string;
  role: string;
  passwordHash: string;
  activeSessionId: string | null;
};

declare global {
  // eslint-disable-next-line no-var
  var __mlAuthUsers: Map<string, AppUser> | undefined;
  // eslint-disable-next-line no-var
  var __mlAuthSeeded: boolean | undefined;
}

function users(): Map<string, AppUser> {
  if (!globalThis.__mlAuthUsers) globalThis.__mlAuthUsers = new Map();
  return globalThis.__mlAuthUsers;
}

export function passwordMap(): Record<string, string> {
  try {
    const raw = process.env.SEED_DEFAULT_PASSWORD_MAP;
    if (raw) return JSON.parse(raw) as Record<string, string>;
  } catch {
    /* ignore */
  }
  const out: Record<string, string> = {};
  for (const m of TEAM_MEMBERS) {
    out[m.email.toLowerCase()] = "Lab@ChangeMe1";
  }
  return out;
}

function fromDb(row: DbUserRow): AppUser {
  return {
    id: row.id,
    email: row.email,
    name: row.name,
    role: row.role,
    passwordHash: row.password_hash,
    activeSessionId: row.active_session_id,
  };
}

function cachePut(user: AppUser): void {
  users().set(user.email.toLowerCase(), user);
}

/**
 * Upsert roster into DB (or memory). overwritePasswords=true forces hashes from seed map
 * (used by POST /api/auth/seed).
 */
export async function ensureSeeded(opts?: { overwritePasswords?: boolean }): Promise<void> {
  const overwrite = Boolean(opts?.overwritePasswords);
  if (!overwrite && globalThis.__mlAuthSeeded && users().size > 0 && !authDbEnabled()) {
    return;
  }
  const pw = passwordMap();
  for (const m of TEAM_MEMBERS) {
    const email = m.email.toLowerCase();
    const role = m.role === "admin" ? "admin" : "scientist";
    const passwordHash = await hashPassword(pw[email] || "Lab@ChangeMe1");

    if (authDbEnabled()) {
      const row = await dbUpsertUser({
        email,
        name: m.name,
        role,
        password_hash: passwordHash,
        overwritePassword: overwrite,
      });
      if (row) cachePut(fromDb(row));
      continue;
    }

    const existing = users().get(email);
    if (existing && !overwrite) continue;
    const id = existing?.id || newId();
    cachePut({
      id,
      email,
      name: m.name,
      role,
      passwordHash,
      activeSessionId: existing?.activeSessionId ?? null,
    });
  }
  globalThis.__mlAuthSeeded = true;
}

export async function findUserByEmail(email: string): Promise<AppUser | null> {
  const canonical = resolveLoginEmail(email);
  if (authDbEnabled()) {
    const row = await dbFindUserByEmail(canonical);
    if (row) {
      const u = fromDb(row);
      cachePut(u);
      return u;
    }
    // Cold start: seed missing roster row without overwriting others
    await ensureSeeded({ overwritePasswords: false });
    const again = await dbFindUserByEmail(canonical);
    if (again) {
      const u = fromDb(again);
      cachePut(u);
      return u;
    }
  }
  await ensureSeeded({ overwritePasswords: false });
  return users().get(canonical) ?? null;
}

export async function setActiveSession(userId: string, sid: string | null): Promise<void> {
  if (authDbEnabled()) {
    await dbSetActiveSession(userId, sid);
  }
  for (const u of users().values()) {
    if (u.id === userId) {
      u.activeSessionId = sid;
      return;
    }
  }
}

export async function updateUserPassword(email: string, newPassword: string): Promise<boolean> {
  const canonical = resolveLoginEmail(email);
  const hash = await hashPassword(newPassword);
  if (authDbEnabled()) {
    const ok = await dbUpdatePassword(canonical, hash);
    if (!ok) return false;
  }
  const u = users().get(canonical);
  if (u) {
    u.passwordHash = hash;
  } else if (!authDbEnabled()) {
    return false;
  }
  // refresh cache from DB if needed
  if (authDbEnabled()) {
    const row = await dbFindUserByEmail(canonical);
    if (row) cachePut(fromDb(row));
  }
  return true;
}

export function isRosterEmail(email: string): boolean {
  const canonical = resolveLoginEmail(email);
  return TEAM_MEMBERS.some((m) => m.email.toLowerCase() === canonical);
}

export function validatePasswordStrength(password: string): string | null {
  if (password.length < 8) return "Password must be at least 8 characters.";
  if (!/[A-Z]/.test(password)) return "Password must include an uppercase letter.";
  if (!/[a-z]/.test(password)) return "Password must include a lowercase letter.";
  if (!/[0-9]/.test(password)) return "Password must include a number.";
  return null;
}
