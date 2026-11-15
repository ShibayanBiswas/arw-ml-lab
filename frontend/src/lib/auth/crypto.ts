import { randomInt, randomUUID } from "crypto";
import { SignJWT, jwtVerify } from "jose";
import bcrypt from "bcryptjs";
import type { NextResponse } from "next/server";

export const COOKIE_NAME = "ml_session";
export const PENDING_COOKIE = "ml_pending";
export const SESSION_MAX_AGE_SEC = 60 * 60 * 12;

function getSecret() {
  const secret = process.env.JWT_SECRET;
  if (!secret) {
    throw new Error("JWT_SECRET is not set");
  }
  return new TextEncoder().encode(secret);
}

function cookieSecure(): boolean {
  return process.env.NODE_ENV === "production" || process.env.VERCEL === "1";
}

const cookieBase = {
  httpOnly: true,
  sameSite: "lax" as const,
  path: "/",
};

export type SessionPayload = {
  userId: string;
  email: string;
  name: string;
  role: string;
  sid: string;
  workspaceId?: string;
};

export type PendingPayload = {
  userId: string;
  email: string;
  name: string;
  purpose: "login" | "password_reset";
  otpId: string;
};

export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, 12);
}

export async function verifyPassword(password: string, hash: string): Promise<boolean> {
  return bcrypt.compare(password, hash);
}

export function generateOtp(): string {
  return String(randomInt(100000, 999999));
}

export function newId(): string {
  return randomUUID();
}

export async function createSessionToken(payload: SessionPayload): Promise<string> {
  return new SignJWT({
    sub: payload.userId,
    userId: payload.userId,
    email: payload.email,
    name: payload.name,
    role: payload.role,
    sid: payload.sid,
    workspaceId: payload.workspaceId,
  })
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setExpirationTime(`${SESSION_MAX_AGE_SEC}s`)
    .sign(getSecret());
}

export async function createPendingToken(payload: PendingPayload): Promise<string> {
  return new SignJWT({ ...payload })
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setExpirationTime("10m")
    .sign(getSecret());
}

export async function verifyToken<T>(token: string): Promise<T | null> {
  try {
    const { payload } = await jwtVerify(token, getSecret());
    return payload as T;
  } catch {
    return null;
  }
}

export function applySessionCookie(res: NextResponse, token: string) {
  res.cookies.set(COOKIE_NAME, token, {
    ...cookieBase,
    secure: cookieSecure(),
    maxAge: SESSION_MAX_AGE_SEC,
  });
}

export function applyPendingCookie(res: NextResponse, token: string) {
  res.cookies.set(PENDING_COOKIE, token, {
    ...cookieBase,
    secure: cookieSecure(),
    maxAge: 60 * 10,
  });
}

export function clearCookiesOnResponse(res: NextResponse) {
  res.cookies.set(COOKIE_NAME, "", { ...cookieBase, secure: cookieSecure(), maxAge: 0 });
  res.cookies.set(PENDING_COOKIE, "", { ...cookieBase, secure: cookieSecure(), maxAge: 0 });
}
