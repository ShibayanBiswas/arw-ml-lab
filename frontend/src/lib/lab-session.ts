/** Dev/auth header helpers for lab-api calls from the browser. */

export function labAuthHeaders(): Record<string, string> {
  return {
    Authorization: "Bearer test",
    "X-Test-Role": "scientist",
    "X-Test-User-Id": "00000000-0000-0000-0000-000000000099",
    "X-Test-Workspace-Id": "00000000-0000-0000-0000-000000000010",
    "Content-Type": "application/json",
  };
}
