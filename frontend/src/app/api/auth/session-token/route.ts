/** Returns Bearer JWT for lab-api calls (same cookie session). */
import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { COOKIE_NAME, verifyToken } from "@/lib/auth/crypto";

export const dynamic = "force-dynamic";

export async function GET() {
  const jar = await cookies();
  const tok = jar.get(COOKIE_NAME)?.value;
  if (!tok) {
    return NextResponse.json({ error: "unauthenticated" }, { status: 401 });
  }
  const session = await verifyToken(tok);
  if (!session) {
    return NextResponse.json({ error: "unauthenticated" }, { status: 401 });
  }
  return NextResponse.json({ access_token: tok });
}
