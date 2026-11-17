import { describe, expect, it } from "vitest";
import { suitabilityPlotPath } from "./api";

describe("suitabilityPlotPath", () => {
  it("maps FS.P catalogue slugs to lab-api suitability plot routes", () => {
    expect(suitabilityPlotPath("volatility")).toBe("/api/v1/suitability/plots/volatility");
    expect(suitabilityPlotPath("price")).toBe("/api/v1/suitability/plots/price");
    expect(suitabilityPlotPath("barriers")).toBe("/api/v1/suitability/plots/barriers");
    expect(suitabilityPlotPath("uniqueness")).toBe("/api/v1/suitability/plots/uniqueness");
    expect(suitabilityPlotPath("holding")).toBe("/api/v1/suitability/plots/holding");
    expect(suitabilityPlotPath("min-ffd")).toBe("/api/v1/suitability/plots/min-ffd");
    expect(suitabilityPlotPath("sadf")).toBe("/api/v1/suitability/plots/sadf");
    expect(suitabilityPlotPath("trendscan")).toBe("/api/v1/suitability/plots/trendscan");
    expect(suitabilityPlotPath("label-balance")).toBe("/api/v1/suitability/plots/label-balance");
    expect(suitabilityPlotPath("grid")).toBe("/api/v1/suitability/plots/grid");
  });
});