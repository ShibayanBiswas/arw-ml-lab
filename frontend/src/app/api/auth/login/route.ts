import { NextResponse } from "next/server";
import { z } from "zod";
import { TEAM_MEMBERS, resolveLoginEmail } from "@/data/team";
import {
  verifyPassword,
  createPendingToken,
  applyPendingCookie,
} from "@/lib/auth/crypto";
import { createOtp, ensureSeeded, findUserByEmail } from "@/lib/auth/store";

export const dynamic = "force-dynamic";

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(1),
});

const allowed = new Set(TEAM_MEMBERS.map((m) => m.email.toLowerCase()));

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const parsed = schema.safeParse(body);
    if (!parsed.success) {
      return NextResponse.json({ error: "Invalid email ID." }, { status: 400 });
    }
    const canonical = resolveLoginEmail(parsed.data.email);
    if (!allowed.has(canonical)) {
      return NextResponse.json({ error: "Invalid email ID." }, { status: 401 });
    }
    await ensureSeeded();
    const user = await findUserByEmail(canonical);
    if (!user) {
      return NextResponse.json(
        { error: "Account not provisioned. Set SEED_DEFAULT_PASSWORD_MAP and POST /api/auth/seed." },
        { status: 401 },
      );
    }
    const ok = await verifyPassword(parsed.data.password, user.passwordHash);
    if (!ok) {
      return NextResponse.json({ error: "Wrong password." }, { status: 401 });
    }
    const { otp, code } = await createOtp(user);
    const pending = await createPendingToken({
      userId: user.id,
      email: user.email,
      name: user.name,
      purpose: "login",
      otpId: otp.id,
    });
    const res = NextResponse.json({
      ok: true,
      otp: code,
      email: user.email,
      name: user.name,
    });
    applyPendingCookie(res, pending);
    return res;
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}
