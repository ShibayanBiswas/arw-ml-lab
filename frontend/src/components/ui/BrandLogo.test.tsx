import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { BrandLogo } from "@/components/ui/BrandLogo";

vi.mock("@/lib/theme", () => ({
  useTheme: () => ({ theme: "dark", toggleTheme: vi.fn() }),
}));

vi.mock("next/image", () => ({
  default: (props: { alt: string; className?: string; src: string }) => (
    // eslint-disable-next-line @next/next/no-img-element
    <img alt={props.alt} className={props.className} src={props.src} />
  ),
}));

describe("BrandLogo", () => {
  it("renders ARWL wordmark and inverts on dark theme", () => {
    render(<BrandLogo />);
    const img = screen.getByAltText("Anand Rathi Wealth");
    expect(img.getAttribute("src")).toContain("arwl-logo.png");
    expect(img.className).toContain("invert");
  });
});
