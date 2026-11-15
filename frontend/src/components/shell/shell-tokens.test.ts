import { readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";

describe("SP shell tokens", () => {
  const css = readFileSync(
    path.join(__dirname, "../../app/globals.css"),
    "utf8"
  );

  it("includes gold and font tokens from SP Workstation", () => {
    expect(css).toContain("--gold: #c9a227");
    expect(css).toContain("--font-display");
    expect(css).toContain("Cormorant Garamond");
    expect(css).toContain("DM Sans");
    expect(css).toContain("IBM Plex Mono");
    expect(css).toContain("--sidebar-width: 280px");
    expect(css).toContain("--sidebar-collapsed-width: 76px");
  });

  it("includes panel-luxe and shell utility classes", () => {
    expect(css).toContain(".panel-luxe");
    expect(css).toContain(".section-kicker");
    expect(css).toContain(".status-pill");
    expect(css).toContain(".live-sync-pill");
    expect(css).toContain(".module-tile");
    expect(css).toContain(".tape-chip");
    expect(css).toContain(".animate-rise");
    expect(css).toContain(".dashboard-shell");
    expect(css).toContain(".dashboard-shell-collapsed");
  });
});
