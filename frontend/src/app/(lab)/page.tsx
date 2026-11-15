import { cookies } from "next/headers";
import { HomeTerminal } from "@/components/home/HomeTerminal";
import { COOKIE_NAME, verifyToken, type SessionPayload } from "@/lib/auth/crypto";

export default async function HomeTerminalPage() {
  let userName = "Lab User";
  const bypass =
    process.env.LAB_AUTH_BYPASS === "true" ||
    process.env.NEXT_PUBLIC_LAB_AUTH_BYPASS === "true";

  if (!bypass && process.env.JWT_SECRET) {
    const jar = await cookies();
    const tok = jar.get(COOKIE_NAME)?.value;
    const session = tok ? await verifyToken<SessionPayload>(tok) : null;
    if (session) {
      userName = session.name || session.email?.split("@")[0] || "Lab User";
    }
  }

  return <HomeTerminal userName={userName} />;
}
