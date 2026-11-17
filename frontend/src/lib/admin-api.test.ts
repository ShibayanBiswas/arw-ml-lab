import { describe, expect, it } from "vitest";
import { adminAuditExportPath, adminAuditPath } from "./api";

describe("adminAuditPath", () => {
  it("maps to lab-api admin audit routes", () => {
    expect(adminAuditPath()).toBe("/api/v1/admin/audit");
    expect(adminAuditExportPath()).toBe("/api/v1/admin/audit/export");
  });
});