import { describe, expect, it } from "vitest";
import { unsupervisedAnomalyPlotPath, unsupervisedClusteringPlotPath } from "./api";

describe("unsupervisedAnomalyPlotPath", () => {
  it("maps catalogue plot slugs to lab-api routes", () => {
    expect(unsupervisedAnomalyPlotPath("score-hist")).toBe(
      "/api/v1/unsupervised/anomaly/score-hist"
    );
    expect(unsupervisedAnomalyPlotPath("ranked")).toBe("/api/v1/unsupervised/anomaly/ranked");
    expect(unsupervisedAnomalyPlotPath("embed")).toBe("/api/v1/unsupervised/anomaly/embed");
  });
});

describe("unsupervisedClusteringPlotPath", () => {
  it("maps CLU catalogue slugs to lab-api clustering routes", () => {
    expect(unsupervisedClusteringPlotPath("elbow")).toBe("/api/v1/unsupervised/clustering/elbow");
    expect(unsupervisedClusteringPlotPath("silhouette")).toBe(
      "/api/v1/unsupervised/clustering/silhouette"
    );
    expect(unsupervisedClusteringPlotPath("ch")).toBe("/api/v1/unsupervised/clustering/ch");
    expect(unsupervisedClusteringPlotPath("db")).toBe("/api/v1/unsupervised/clustering/db");
    expect(unsupervisedClusteringPlotPath("gap")).toBe("/api/v1/unsupervised/clustering/gap");
    expect(unsupervisedClusteringPlotPath("dendrogram")).toBe(
      "/api/v1/unsupervised/clustering/dendrogram"
    );
  });
});