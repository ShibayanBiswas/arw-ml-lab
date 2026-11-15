import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

/** OTP login removed (Phase 2-cont-3 / ADR-0008). */
export async function POST() {
  return NextResponse.json(
    { error: "OTP login removed. Sign in with email and password." },
    { status: 410 },
  );
}
