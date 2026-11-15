import { redirect } from "next/navigation";

/** OTP login removed (Phase 2-cont-3) — password-only session. */
export default function OtpRedirectPage() {
  redirect("/login");
}
