import { describe, expect, it } from "vitest";
import { EDA_EXPLANATIONS, resolveExplanation } from "./eda";

describe("explanations registry", () => {
  it("covers core EDA table keys", () => {
    const keys = new Set(EDA_EXPLANATIONS.map((e) => e.key));
    expect(keys.has("table.eda.overview")).toBe(true);
    expect(keys.has("table.eda.missing")).toBe(true);
    expect(keys.has("table.eda.stationarity")).toBe(true);
  });

  it("resolves edu keys", () => {
    const e = resolveExplanation("table.eda.overview");
    expect(e?.title).toContain("overview");
    expect(e?.math.length).toBeGreaterThan(0);
  });
});
