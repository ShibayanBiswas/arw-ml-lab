/**
 * Server-only Supabase service-role client for lab_app_users.
 * Never import from client components. Key must not be NEXT_PUBLIC_*.
 */
import { createClient, type SupabaseClient } from "@supabase/supabase-js";

export type DbUserRow = {
  id: string;
  email: string;
  name: string;
  role: string;
  password_hash: string;
  active_session_id: string | null;
};

let cached: SupabaseClient | null | undefined;

export function authDbEnabled(): boolean {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
  return Boolean(url && key);
}

export function getAuthDb(): SupabaseClient | null {
  if (cached !== undefined) return cached;
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!url || !key) {
    cached = null;
    return null;
  }
  cached = createClient(url, key, {
    auth: { persistSession: false, autoRefreshToken: false },
  });
  return cached;
}

export async function dbFindUserByEmail(email: string): Promise<DbUserRow | null> {
  const db = getAuthDb();
  if (!db) return null;
  const { data, error } = await db
    .from("lab_app_users")
    .select("id,email,name,role,password_hash,active_session_id")
    .eq("email", email.toLowerCase())
    .maybeSingle();
  if (error || !data) return null;
  return data as DbUserRow;
}

export async function dbUpsertUser(row: {
  email: string;
  name: string;
  role: string;
  password_hash: string;
  overwritePassword?: boolean;
}): Promise<DbUserRow | null> {
  const db = getAuthDb();
  if (!db) return null;
  const email = row.email.toLowerCase();
  const existing = await dbFindUserByEmail(email);
  if (existing && !row.overwritePassword) {
    return existing;
  }
  if (existing) {
    const { data, error } = await db
      .from("lab_app_users")
      .update({
        name: row.name,
        role: row.role,
        password_hash: row.password_hash,
        updated_at: new Date().toISOString(),
      })
      .eq("email", email)
      .select("id,email,name,role,password_hash,active_session_id")
      .single();
    if (error || !data) return null;
    return data as DbUserRow;
  }
  const { data, error } = await db
    .from("lab_app_users")
    .insert({
      email,
      name: row.name,
      role: row.role,
      password_hash: row.password_hash,
    })
    .select("id,email,name,role,password_hash,active_session_id")
    .single();
  if (error || !data) return null;
  return data as DbUserRow;
}

export async function dbUpdatePassword(email: string, password_hash: string): Promise<boolean> {
  const db = getAuthDb();
  if (!db) return false;
  const { error } = await db
    .from("lab_app_users")
    .update({ password_hash, updated_at: new Date().toISOString() })
    .eq("email", email.toLowerCase());
  return !error;
}

export async function dbSetActiveSession(userId: string, sid: string | null): Promise<void> {
  const db = getAuthDb();
  if (!db) return;
  await db
    .from("lab_app_users")
    .update({ active_session_id: sid, updated_at: new Date().toISOString() })
    .eq("id", userId);
}
