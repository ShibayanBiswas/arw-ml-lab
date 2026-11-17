import { describe, expect, it } from "vitest";
import { unsupervisedAnomalyPlotPath } from "./api";

describe("unsupervisedAnomalyPlotPath", () => {
  it("maps catalogue plot slugs to lab-api routes", () => {
    expect(unsupervisedAnomalyPlotPath("score-hist")).toBe(
      "/api/v1/unsupervised/anomaly/score-hist"
    );
    expect(unsupervisedAnomalyPlotPath("ranked")).toBe("/api/v1/unsupervised/anomaly/ranked");
    expect(unsupervisedAnomalyPlotPath("embed")).toBe("/api/v1/unsupervised/anomaly/embed");
  });
});