import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { HomeTerminal } from "@/components/home/HomeTerminal";
import { ModuleHub } from "@/components/home/ModuleHub";
import { MODULES } from "@/lib/modules";

vi.mock("@/components/jobs/JobProgress", () => ({
  JobProgress: () => <div data-testid="job-progress-stub" />,
}));

describe("HomeTerminal", () => {
  it("renders greeting, gallery, and ARWL footer without apologetic copy", () => {
    render(<HomeTerminal userName="Shibayan" />);
    expect(screen.getByTestId("home-terminal")).toBeTruthy();
    expect(screen.getByTestId("home-greeting").textContent).toContain("Shibayan");
    expect(screen.getByTestId("module-gallery")).toBeTruthy();
    expect(screen.getByText(/ANAND RATHI WEALTH · MACHINE LEARNING LAB/i)).toBeTruthy();
    expect(screen.queryByText(/arrives in later phases/i)).toBeNull();
  });
});

describe("ModuleHub", () => {
  it("lists submodule cards from registry", () => {
    const mod = MODULES.find((m) => m.id === "data")!;
    render(<ModuleHub mod={mod} />);
    expect(screen.getByTestId("module-hub").getAttribute("data-module")).toBe("data");
    expect(screen.getByText("Sample Datasets")).toBeTruthy();
    expect(screen.getByText("Upload")).toBeTruthy();
  });
});
