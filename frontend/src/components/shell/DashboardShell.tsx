"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { Menu, PanelLeftClose, PanelLeftOpen } from "lucide-react";
import { Sidebar } from "@/components/shell/Sidebar";

type ShellContextValue = {
  collapsed: boolean;
  mobileOpen: boolean;
  toggleCollapsed: () => void;
  setMobileOpen: (open: boolean) => void;
};

const ShellContext = createContext<ShellContextValue | null>(null);
const COLLAPSE_KEY = "arw-sidebar-collapsed";

export function useDashboardShell() {
  const ctx = useContext(ShellContext);
  if (!ctx) throw new Error("useDashboardShell must be used within DashboardShell");
  return ctx;
}

type Props = {
  userName: string;
  userEmail: string;
  children: ReactNode;
};

export function DashboardShell({ userName, userEmail, children }: Props) {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const frame = window.requestAnimationFrame(() => {
      setCollapsed(window.localStorage.getItem(COLLAPSE_KEY) === "1");
      setReady(true);
    });
    return () => window.cancelAnimationFrame(frame);
  }, []);

  useEffect(() => {
    function onResize() {
      if (window.innerWidth >= 1024) setMobileOpen(false);
    }
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

  const toggleCollapsed = useCallback(() => {
    setCollapsed((prev) => {
      const next = !prev;
      window.localStorage.setItem(COLLAPSE_KEY, next ? "1" : "0");
      return next;
    });
  }, []);

  const value = useMemo(
    () => ({ collapsed, mobileOpen, toggleCollapsed, setMobileOpen }),
    [collapsed, mobileOpen, toggleCollapsed]
  );

  return (
    <ShellContext.Provider value={value}>
      <div
        className={`dashboard-shell dashboard-shell-alive ${collapsed ? "dashboard-shell-collapsed" : ""} ${ready ? "dashboard-shell-ready" : ""}`}
        data-testid="dashboard-shell"
        data-collapsed={collapsed ? "1" : "0"}
      >
        <header className="dashboard-mobile-bar lg:hidden">
          <button
            type="button"
            className="dashboard-icon-btn"
            aria-label="Open menu"
            onClick={() => setMobileOpen(true)}
          >
            <Menu size={18} />
          </button>
          <span className="font-[family-name:var(--font-display)] text-lg">ARW ML Lab</span>
          <button
            type="button"
            className="dashboard-icon-btn"
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
            onClick={toggleCollapsed}
          >
            {collapsed ? <PanelLeftOpen size={18} /> : <PanelLeftClose size={18} />}
          </button>
        </header>

        {mobileOpen ? (
          <button
            type="button"
            className="dashboard-sidebar-backdrop"
            aria-label="Close menu"
            onClick={() => setMobileOpen(false)}
          />
        ) : null}

        <aside
          className={`dashboard-sidebar ${mobileOpen ? "dashboard-sidebar-open" : ""}`}
          data-testid="sidebar"
        >
          <div className="hidden items-center justify-end px-2 pt-2 lg:flex">
            <button
              type="button"
              className="dashboard-icon-btn"
              aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
              data-testid="sidebar-collapse"
              onClick={toggleCollapsed}
            >
              {collapsed ? <PanelLeftOpen size={16} /> : <PanelLeftClose size={16} />}
            </button>
          </div>
          <Sidebar
            userName={userName}
            userEmail={userEmail}
            collapsed={collapsed}
            onNavigate={() => setMobileOpen(false)}
          />
        </aside>

        <main className="dashboard-main min-h-0 overflow-auto p-4 md:p-6">{children}</main>
      </div>
    </ShellContext.Provider>
  );
}
