/** Auth headers for lab-api calls from the browser. */

const DEFAULT_WS = "00000000-0000-0000-0000-000000000010";

let cachedToken: string | null = null;

export function labAuthHeadersSync(): Record<string, string> {
  // Sync path for tests / SSR fallback — bypass when env set
  if (process.env.NEXT_PUBLIC_LAB_AUTH_BYPASS === "true" || process.env.AUTH_TEST_BYPASS === "true") {
    return {
      Authorization: "Bearer test",
      "X-Test-Role": "scientist",
      "X-Test-User-Id": "00000000-0000-0000-0000-000000000099",
      "X-Test-Workspace-Id": DEFAULT_WS,
      "Content-Type": "application/json",
    };
  }
  const h: Record<string, string> = { "Content-Type": "application/json" };
  if (cachedToken) {
    h.Authorization = `Bearer ${cachedToken}`;
    h["X-Workspace-Id"] = DEFAULT_WS;
  }
  return h;
}

/** @deprecated use labAuthHeadersSync or await labAuthHeaders */
export function labAuthHeaders(): Record<string, string> {
  return labAuthHeadersSync();
}

export async function labAuthHeadersAsync(): Promise<Record<string, string>> {
  if (typeof window === "undefined") {
    return labAuthHeadersSync();
  }
  if (process.env.NEXT_PUBLIC_LAB_AUTH_BYPASS === "true") {
    return labAuthHeadersSync();
  }
  try {
    const res = await fetch("/api/auth/session-token", { credentials: "include" });
    if (res.ok) {
      const data = (await res.json()) as { access_token?: string };
      if (data.access_token) {
        cachedToken = data.access_token;
        return {
          Authorization: `Bearer ${data.access_token}`,
          "X-Workspace-Id": DEFAULT_WS,
          "Content-Type": "application/json",
        };
      }
    }
  } catch {
    /* fall through */
  }
  // Dev convenience when JWT_SECRET local + AUTH_TEST_BYPASS on API
  return labAuthHeadersSync();
}
