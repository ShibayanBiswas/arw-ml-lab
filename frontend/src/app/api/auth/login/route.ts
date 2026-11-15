import { NextResponse } from "next/server";
import { z } from "zod";
import { TEAM_MEMBERS, resolveLoginEmail } from "@/data/team";
import {
  verifyPassword,
  createSessionToken,
  applySessionCookie,
  clearCookiesOnResponse,
  newId,
} from "@/lib/auth/crypto";
import { ensureSeeded, findUserByEmail, setActiveSession } from "@/lib/auth/store";

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
    await ensureSeeded({ overwritePasswords: false });
    const user = await findUserByEmail(canonical);
    if (!user) {
      return NextResponse.json(
        {
          error:
            "Account not provisioned. Set SEED_DEFAULT_PASSWORD_MAP and POST /api/auth/seed.",
        },
        { status: 401 },
      );
    }
    const ok = await verifyPassword(parsed.data.password, user.passwordHash);
    if (!ok) {
      return NextResponse.json({ error: "Wrong password." }, { status: 401 });
    }
    const sid = newId();
    await setActiveSession(user.id, sid);
    const token = await createSessionToken({
      userId: user.id,
      email: user.email,
      name: user.name,
      role: user.role,
      sid,
      workspaceId:
        process.env.LAB_DEFAULT_WORKSPACE_ID || "00000000-0000-0000-0000-000000000010",
    });
    const res = NextResponse.json({
      ok: true,
      email: user.email,
      name: user.name,
      redirect: "/",
    });
    clearCookiesOnResponse(res);
    applySessionCookie(res, token);
    return res;
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}
