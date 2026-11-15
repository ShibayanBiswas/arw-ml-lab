import { describe, expect, it } from "vitest";
import { MODULE_COUNT, MODULES } from "./modules";

describe("module registry", () => {
  it("exposes 12 module groups plus Home Terminal (=13 sidebar entries)", () => {
    expect(MODULES).toHaveLength(12);
    expect(MODULE_COUNT).toBe(13);
  });

  it("every module has nested sub-pages", () => {
    for (const mod of MODULES) {
      expect(mod.nav.length).toBeGreaterThan(0);
      expect(mod.href).toMatch(/^\//);
    }
  });
});
