import { beforeEach, describe, expect, it } from "vitest";
import {
  ensureSeeded,
  findUserByEmail,
  updateUserPassword,
  validatePasswordStrength,
} from "@/lib/auth/store";
import { verifyPassword } from "@/lib/auth/crypto";

describe("auth store (memory path)", () => {
  beforeEach(() => {
    globalThis.__mlAuthUsers = new Map();
    globalThis.__mlAuthSeeded = false;
    delete process.env.SEED_DEFAULT_PASSWORD_MAP;
    delete process.env.SUPABASE_SERVICE_ROLE_KEY;
  });

  it("seeds default password Lab@ChangeMe1", async () => {
    process.env.JWT_SECRET = process.env.JWT_SECRET || "test-secret-for-vitest-32chars!!";
    await ensureSeeded({ overwritePasswords: true });
    const user = await findUserByEmail("shibayanbiswas@rathi.com");
    expect(user).not.toBeNull();
    expect(await verifyPassword("Lab@ChangeMe1", user!.passwordHash)).toBe(true);
    expect(await verifyPassword("wrong", user!.passwordHash)).toBe(false);
  });

  it("respects SEED_DEFAULT_PASSWORD_MAP", async () => {
    process.env.JWT_SECRET = process.env.JWT_SECRET || "test-secret-for-vitest-32chars!!";
    process.env.SEED_DEFAULT_PASSWORD_MAP = JSON.stringify({
      "shibayanbiswas@rathi.com": "Shibayan@123",
    });
    await ensureSeeded({ overwritePasswords: true });
    const user = await findUserByEmail("shibayanbiswas@rathi.com");
    expect(await verifyPassword("Shibayan@123", user!.passwordHash)).toBe(true);
  });

  it("updates password", async () => {
    process.env.JWT_SECRET = process.env.JWT_SECRET || "test-secret-for-vitest-32chars!!";
    await ensureSeeded({ overwritePasswords: true });
    const ok = await updateUserPassword("shibayanbiswas@rathi.com", "NewPass@99");
    expect(ok).toBe(true);
    const user = await findUserByEmail("shibayanbiswas@rathi.com");
    expect(await verifyPassword("NewPass@99", user!.passwordHash)).toBe(true);
  });

  it("validates password strength", () => {
    expect(validatePasswordStrength("short")).toBeTruthy();
    expect(validatePasswordStrength("Shibayan@123")).toBeNull();
  });
});
