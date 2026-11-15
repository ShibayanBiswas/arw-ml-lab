import { redirect } from "next/navigation";
import { cookies } from "next/headers";
import { DashboardShell } from "@/components/shell/DashboardShell";
import { COOKIE_NAME, verifyToken, type SessionPayload } from "@/lib/auth/crypto";

export default async function LabLayout({ children }: { children: React.ReactNode }) {
  const bypass =
    process.env.LAB_AUTH_BYPASS === "true" ||
    process.env.NEXT_PUBLIC_LAB_AUTH_BYPASS === "true";

  let userName = "Lab User";
  let userEmail = "dev@localhost";

  if (!bypass) {
    if (!process.env.JWT_SECRET) {
      // Local UI without JWT yet
      redirect("/login");
    }
    const jar = await cookies();
    const tok = jar.get(COOKIE_NAME)?.value;
    const session = tok ? await verifyToken<SessionPayload>(tok) : null;
    if (!session) {
      redirect("/login");
    }
    userName = session.name || session.email?.split("@")[0] || "Lab User";
    userEmail = session.email || "user@rathi.com";
  }

  return (
    <DashboardShell userName={userName} userEmail={userEmail}>
      {children}
    </DashboardShell>
  );
}
