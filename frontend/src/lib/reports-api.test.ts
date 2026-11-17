import { describe, expect, it } from "vitest";
import { reportsNotebookPath } from "./api";

describe("reportsNotebookPath", () => {
  it("maps to lab-api reproduction notebook route", () => {
    expect(reportsNotebookPath()).toBe("/api/v1/reports/notebook");
  });
});