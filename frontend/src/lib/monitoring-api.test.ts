import { describe, expect, it } from "vitest";
import { monitoringKsDriftPath, monitoringPsiDriftPath } from "./api";

describe("monitoringKsDriftPath", () => {
  it("maps to lab-api KS drift route", () => {
    expect(monitoringKsDriftPath()).toBe("/api/v1/monitoring/drift/ks");
  });
});

describe("monitoringPsiDriftPath", () => {
  it("maps to lab-api PSI drift route", () => {
    expect(monitoringPsiDriftPath()).toBe("/api/v1/monitoring/drift/psi");
  });
});