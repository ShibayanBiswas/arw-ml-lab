import { describe, expect, it } from "vitest";
import { monitoringKsDriftPath } from "./api";

describe("monitoringKsDriftPath", () => {
  it("maps to lab-api KS drift route", () => {
    expect(monitoringKsDriftPath()).toBe("/api/v1/monitoring/drift/ks");
  });
});