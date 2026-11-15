import { NextResponse } from "next/server";
import { z } from "zod";
import { cookies } from "next/headers";
import {
  PENDING_COOKIE,
  verifyToken,
  createSessionToken,
  applySessionCookie,
  clearCookiesOnResponse,
  newId,
  type PendingPayload,
} from "@/lib/auth/crypto";
import { consumeOtp, setActiveSession } from "@/lib/auth/store";

export const dynamic = "force-dynamic";

const schema = z.object({ code: z.string().length(6) });

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const parsed = schema.safeParse(body);
    if (!parsed.success) {
      return NextResponse.json({ error: "Invalid code." }, { status: 400 });
    }
    const jar = await cookies();
    const pendingTok = jar.get(PENDING_COOKIE)?.value;
    if (!pendingTok) {
      return NextResponse.json({ error: "Session expired. Sign in again." }, { status: 401 });
    }
    const pending = await verifyToken<PendingPayload>(pendingTok);
    if (!pending || pending.purpose !== "login") {
      return NextResponse.json({ error: "Session expired. Sign in again." }, { status: 401 });
    }
    const otp = await consumeOtp(pending.otpId, parsed.data.code);
    if (!otp) {
      return NextResponse.json({ error: "Invalid or expired code." }, { status: 401 });
    }
    const sid = newId();
    await setActiveSession(pending.userId, sid);
    const token = await createSessionToken({
      userId: pending.userId,
      email: pending.email,
      name: pending.name,
      role: "scientist",
      sid,
      workspaceId: process.env.LAB_DEFAULT_WORKSPACE_ID || "00000000-0000-0000-0000-000000000010",
    });
    const res = NextResponse.json({ ok: true, email: pending.email, name: pending.name });
    clearCookiesOnResponse(res);
    applySessionCookie(res, token);
    return res;
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}
