import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { LoginForm } from "@/components/auth/LoginForm";
import { ThemeProvider } from "@/lib/theme";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace: vi.fn(), refresh: vi.fn(), push: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
}));

describe("LoginForm", () => {
  it("renders SP-style card with Change password and no OTP copy", () => {
    render(
      <ThemeProvider>
        <LoginForm />
      </ThemeProvider>,
    );
    expect(screen.getByTestId("login-form")).toHaveClass("auth-card-large");
    expect(screen.getByRole("link", { name: /change password/i })).toHaveAttribute(
      "href",
      "/change-password",
    );
    expect(screen.queryByText(/on-screen otp/i)).toBeNull();
    expect(screen.queryByText(/local otp/i)).toBeNull();
    expect(screen.getByLabelText(/user id \/ email/i)).toBeTruthy();
  });
});
