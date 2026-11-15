import { NextResponse } from "next/server";
import { ensureSeeded } from "@/lib/auth/store";
import { TEAM_MEMBERS } from "@/data/team";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  const secret = request.headers.get("x-seed-secret");
  if (!secret || secret !== process.env.JWT_SECRET) {
    return NextResponse.json({ error: "forbidden" }, { status: 403 });
  }
  await ensureSeeded();
  return NextResponse.json({ ok: true, users: TEAM_MEMBERS.length });
}
