import { NextResponse } from "next/server";
import { z } from "zod";
import { resolveLoginEmail } from "@/data/team";
import { verifyPassword, clearCookiesOnResponse } from "@/lib/auth/crypto";
import {
  findUserByEmail,
  isRosterEmail,
  updateUserPassword,
  validatePasswordStrength,
} from "@/lib/auth/store";

export const dynamic = "force-dynamic";

const schema = z.object({
  email: z.string().email(),
  currentPassword: z.string().min(1),
  newPassword: z.string().min(1),
});

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const parsed = schema.safeParse(body);
    if (!parsed.success) {
      return NextResponse.json({ error: "Invalid request." }, { status: 400 });
    }
    const canonical = resolveLoginEmail(parsed.data.email);
    if (!isRosterEmail(canonical)) {
      return NextResponse.json({ error: "Invalid email ID." }, { status: 401 });
    }
    const strength = validatePasswordStrength(parsed.data.newPassword);
    if (strength) {
      return NextResponse.json({ error: strength }, { status: 400 });
    }
    const user = await findUserByEmail(canonical);
    if (!user) {
      return NextResponse.json({ error: "Account not provisioned." }, { status: 401 });
    }
    const ok = await verifyPassword(parsed.data.currentPassword, user.passwordHash);
    if (!ok) {
      return NextResponse.json({ error: "Wrong password." }, { status: 401 });
    }
    const updated = await updateUserPassword(canonical, parsed.data.newPassword);
    if (!updated) {
      return NextResponse.json({ error: "Unable to update password." }, { status: 500 });
    }
    const res = NextResponse.json({ ok: true, email: canonical });
    clearCookiesOnResponse(res);
    return res;
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}
