import { describe, expect, it } from "vitest";
import { reportsExecutivePath, reportsNotebookPath } from "./api";

describe("reportsNotebookPath", () => {
  it("maps to lab-api reproduction notebook route", () => {
    expect(reportsNotebookPath()).toBe("/api/v1/reports/notebook");
  });
});

describe("reportsExecutivePath", () => {
  it("maps to lab-api executive summary route", () => {
    expect(reportsExecutivePath()).toBe("/api/v1/reports/executive");
    expect(reportsExecutivePath(true)).toBe("/api/v1/reports/executive?include_pdf=true");
  });
});