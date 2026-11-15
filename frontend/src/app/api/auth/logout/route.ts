import { NextResponse } from "next/server";
import { clearCookiesOnResponse } from "@/lib/auth/crypto";

export const dynamic = "force-dynamic";

export async function POST() {
  const res = NextResponse.json({ ok: true });
  clearCookiesOnResponse(res);
  return res;
}
