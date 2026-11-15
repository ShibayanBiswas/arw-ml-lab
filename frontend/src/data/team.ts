export type TeamMemberSeed = {
  name: string;
  email: string;
  role: "admin" | "scientist" | "member";
};

/** Same roster as SP Workstation — Rathi mail allowlist. */
export const TEAM_MEMBERS: TeamMemberSeed[] = [
  { name: "Kalpesh Koradia", email: "kalpeshkoradia@rathi.com", role: "member" },
  { name: "Vinay Rathi", email: "vinayrathi@rathi.com", role: "admin" },
  { name: "Sammedi Shah", email: "sammedishah@rathi.com", role: "member" },
  { name: "Parth Parekh", email: "parthparekh@rathi.com", role: "member" },
  { name: "Nishchay Soni", email: "nishchaysoni@rathi.com", role: "member" },
  { name: "Subhendu Maji", email: "subhendumaji@rathi.com", role: "member" },
  { name: "Shibayan Biswas", email: "shibayanbiswas@rathi.com", role: "admin" },
  { name: "Feroze Azeez", email: "ferozeazeez@rathi.com", role: "member" },
];

const LOGIN_EMAIL_ALIASES: Record<string, string> = {
  "shiabaynbiswas@rathi.com": "shibayanbiswas@rathi.com",
};

export function resolveLoginEmail(email: string): string {
  const low = email.toLowerCase().trim();
  return LOGIN_EMAIL_ALIASES[low] ?? low;
}
