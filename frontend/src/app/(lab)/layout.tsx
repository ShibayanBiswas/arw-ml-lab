import { redirect } from "next/navigation";
import { DashboardShell } from "@/components/shell/DashboardShell";
import { createClient } from "@/lib/supabase/server";

export default async function LabLayout({ children }: { children: React.ReactNode }) {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  // Dev bypass when Supabase is not configured (Phase 0 local UI work)
  const bypass =
    process.env.LAB_AUTH_BYPASS === "true" ||
    !process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ||
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY === "public-anon-key";

  if (!user && !bypass) {
    redirect("/login");
  }

  const userName =
    (user?.user_metadata?.full_name as string | undefined) ||
    user?.email?.split("@")[0] ||
    "Lab User";
  const userEmail = user?.email ?? "dev@localhost";

  return (
    <DashboardShell userName={userName} userEmail={userEmail}>
      {children}
    </DashboardShell>
  );
}
