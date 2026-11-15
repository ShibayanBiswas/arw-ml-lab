"use client";

import { Greeting } from "@/components/home/Greeting";
import { ModuleGallery } from "@/components/home/ModuleGallery";
import { TerminalHeader } from "@/components/home/TerminalHeader";
import { JobProgress } from "@/components/jobs/JobProgress";

type Props = { userName: string };

export function HomeTerminal({ userName }: Props) {
  return (
    <div
      className="terminal-shell terminal-shell-alive app-alive min-h-full"
      data-testid="home-terminal"
    >
      <div className="terminal-canvas space-y-4 px-0.5 pb-2 sm:space-y-5">
        <div className="animate-rise space-y-3">
          <TerminalHeader />
          <Greeting name={userName} />
        </div>

        <div className="animate-rise-delay-1">
          <ModuleGallery />
        </div>

        <div className="animate-rise-delay-2">
          <JobProgress />
        </div>

        <footer className="home-footer-luxe footer-alive animate-rise-delay-3 border-t border-[color-mix(in_srgb,var(--gold)_14%,var(--border))] px-2 pt-3 pb-[max(0.35rem,env(safe-area-inset-bottom))] text-center text-[9px] tracking-[0.12em] text-[var(--fg-subtle)] sm:text-[10px] sm:tracking-[0.22em]">
          ANAND RATHI WEALTH · MACHINE LEARNING LAB
        </footer>
      </div>
    </div>
  );
}
