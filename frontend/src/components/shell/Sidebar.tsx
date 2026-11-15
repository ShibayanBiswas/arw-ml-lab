"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useMemo, useState, type Dispatch, type SetStateAction } from "react";
import {
  BarChart3,
  Brain,
  ChevronDown,
  Database,
  FileText,
  FlaskConical,
  GraduationCap,
  LayoutDashboard,
  Layers,
  LineChart,
  LogOut,
  Moon,
  Search,
  Shield,
  SlidersHorizontal,
  Sparkles,
  Sun,
} from "lucide-react";
import {
  MODULES,
  collectNavPaths,
  type ModuleGroup,
  type NavItem,
} from "@/lib/modules";
import { useTheme } from "@/lib/theme";
import { createClient } from "@/lib/supabase/client";

const MODULE_ICONS: Record<ModuleGroup["icon"], typeof BarChart3> = {
  database: Database,
  chart: BarChart3,
  sliders: SlidersHorizontal,
  brain: Brain,
  layers: Layers,
  lineChart: LineChart,
  search: Search,
  sparkles: Sparkles,
  flask: FlaskConical,
  fileText: FileText,
  graduation: GraduationCap,
  shield: Shield,
};

type Props = {
  userName: string;
  userEmail: string;
  collapsed?: boolean;
  onNavigate?: () => void;
};

function pathActive(pathname: string, path?: string) {
  if (!path) return false;
  return pathname === path || pathname.startsWith(`${path}/`);
}

function branchActive(pathname: string, item: NavItem) {
  return collectNavPaths(item).some(
    (p) => pathname === p || pathname.startsWith(`${p}/`)
  );
}

function NavBranch({
  item,
  openMap,
  setOpenMap,
  collapsed,
  onNavigate,
}: {
  item: NavItem;
  openMap: Record<string, boolean>;
  setOpenMap: Dispatch<SetStateAction<Record<string, boolean>>>;
  collapsed?: boolean;
  onNavigate?: () => void;
}) {
  const pathname = usePathname();
  const hasChildren = Boolean(item.children?.length);
  const open = !collapsed && (openMap[item.id] ?? false);
  const active = pathActive(pathname, item.path);
  const childActive = hasChildren && branchActive(pathname, item);

  const rowClass = `group flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left transition-all duration-200 ${
    active
      ? "bg-[color-mix(in_srgb,var(--gold)_18%,transparent)] text-[var(--fg)] shadow-[inset_2px_0_0_0_color-mix(in_srgb,var(--gold)_70%,transparent)]"
      : childActive
        ? "text-[var(--fg)]"
        : "text-[var(--fg-subtle)] hover:bg-[var(--bg-muted)] hover:text-[var(--fg)]"
  }`;

  return (
    <div className="my-0.5">
      <div className={rowClass}>
        {item.path ? (
          <Link
            href={item.path}
            className="min-w-0 flex-1 truncate text-[13px] font-medium"
            title={item.description || item.label}
            onClick={() => onNavigate?.()}
          >
            {item.label}
          </Link>
        ) : (
          <button
            type="button"
            className="min-w-0 flex-1 truncate text-left text-[13px] font-medium"
            onClick={() => setOpenMap((s) => ({ ...s, [item.id]: !s[item.id] }))}
          >
            {item.label}
          </button>
        )}
        {hasChildren && !collapsed ? (
          <button
            type="button"
            aria-label={open ? `Collapse ${item.label}` : `Expand ${item.label}`}
            aria-expanded={open}
            className="shrink-0 rounded-md p-1 text-[var(--fg-subtle)]"
            onClick={() => setOpenMap((s) => ({ ...s, [item.id]: !s[item.id] }))}
          >
            <ChevronDown size={14} className={open ? "rotate-180" : ""} />
          </button>
        ) : null}
      </div>
      {hasChildren && open ? (
        <div className="ml-3 border-l border-[color-mix(in_srgb,var(--gold)_18%,var(--border))] pl-2">
          {item.children!.map((child) => (
            <NavBranch
              key={child.id}
              item={child}
              openMap={openMap}
              setOpenMap={setOpenMap}
              collapsed={collapsed}
              onNavigate={onNavigate}
            />
          ))}
        </div>
      ) : null}
    </div>
  );
}

export function Sidebar({ userName, userEmail, collapsed = false, onNavigate }: Props) {
  const pathname = usePathname();
  const router = useRouter();
  const { theme, toggleTheme } = useTheme();
  const [openModules, setOpenModules] = useState<Record<string, boolean>>(() =>
    Object.fromEntries(MODULES.map((m) => [m.id, pathname.startsWith(m.href)]))
  );
  const [openNav, setOpenNav] = useState<Record<string, boolean>>({});

  const initials = useMemo(
    () =>
      userName
        .split(" ")
        .map((p) => p[0])
        .join("")
        .slice(0, 2)
        .toUpperCase() || "AR",
    [userName]
  );

  async function logout() {
    const supabase = createClient();
    await supabase.auth.signOut();
    router.push("/login");
    router.refresh();
  }

  return (
    <div className="relative z-[1] flex h-full min-h-0 flex-1 flex-col">
      <div className="sidebar-brand border-b border-[color-mix(in_srgb,var(--gold)_12%,var(--border))] px-3 py-3.5">
        <Link
          href="/"
          className="flex min-w-0 items-center justify-center lg:justify-start"
          onClick={onNavigate}
          title="Home Terminal"
        >
          {collapsed ? (
            <span className="flex h-10 w-10 items-center justify-center rounded-xl gold-gradient text-xs font-bold text-[#111]">
              AR
            </span>
          ) : (
            <span className="font-[family-name:var(--font-display)] text-xl tracking-tight">
              <span className="gold-text">ARW</span> ML Lab
            </span>
          )}
        </Link>
      </div>

      <nav className="flex-1 overflow-y-auto px-2 py-3" aria-label="Primary">
        <Link
          href="/"
          title="Home Terminal"
          onClick={onNavigate}
          className={`mb-2 flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm ${
            collapsed ? "justify-center px-2" : ""
          } ${
            pathname === "/"
              ? "bg-[color-mix(in_srgb,var(--gold)_18%,transparent)] text-[var(--fg)]"
              : "text-[var(--fg-muted)]"
          }`}
        >
          <LayoutDashboard size={15} />
          {!collapsed ? <span className="font-semibold">Home Terminal</span> : null}
        </Link>

        {!collapsed ? (
          <p className="section-kicker mb-2.5 mt-5 px-3">MODULES</p>
        ) : (
          <div className="my-3 h-px bg-[color-mix(in_srgb,var(--gold)_18%,var(--border))]" />
        )}

        {MODULES.map((mod) => {
          const open = !collapsed && (openModules[mod.id] ?? false);
          const active = pathname.startsWith(mod.href);
          const ModuleIcon = MODULE_ICONS[mod.icon];
          return (
            <div key={mod.id} className="mb-1.5">
              <div
                className={`flex w-full items-center gap-2 rounded-xl px-2 py-1.5 text-sm ${
                  collapsed ? "justify-center" : ""
                } ${active ? "bg-[color-mix(in_srgb,var(--gold)_10%,var(--bg-muted))]" : "text-[var(--fg-muted)]"}`}
              >
                <Link
                  href={mod.href}
                  className={`flex min-w-0 items-center gap-3 rounded-lg px-1 py-1 ${collapsed ? "justify-center" : "flex-1"}`}
                  title={mod.label}
                  onClick={onNavigate}
                >
                  <ModuleIcon size={15} />
                  {!collapsed ? (
                    <span className="min-w-0 flex-1 truncate font-semibold">{mod.label}</span>
                  ) : null}
                </Link>
                {!collapsed ? (
                  <button
                    type="button"
                    aria-label={open ? `Collapse ${mod.label}` : `Expand ${mod.label}`}
                    aria-expanded={open}
                    className="shrink-0 rounded-md p-1.5"
                    onClick={() =>
                      setOpenModules((s) => ({ ...s, [mod.id]: !s[mod.id] }))
                    }
                  >
                    <ChevronDown size={14} className={open ? "rotate-180" : ""} />
                  </button>
                ) : null}
              </div>
              {open ? (
                <div className="ml-4 mt-1 border-l border-[color-mix(in_srgb,var(--gold)_16%,var(--border))] pl-2">
                  {mod.nav.map((item) => (
                    <NavBranch
                      key={item.id}
                      item={item}
                      openMap={openNav}
                      setOpenMap={setOpenNav}
                      collapsed={collapsed}
                      onNavigate={onNavigate}
                    />
                  ))}
                </div>
              ) : null}
            </div>
          );
        })}
      </nav>

      <div className="border-t border-[color-mix(in_srgb,var(--gold)_12%,var(--border))] p-3">
        <div
          className={`mb-3 flex items-center gap-3 rounded-xl px-2.5 py-2.5 ${collapsed ? "justify-center" : ""}`}
        >
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full gold-gradient text-xs font-bold text-[#111]">
            {initials}
          </div>
          {!collapsed ? (
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold">{userName}</p>
              <p className="truncate text-[11px] text-[var(--fg-subtle)]">{userEmail}</p>
            </div>
          ) : null}
        </div>
        <div className={`flex gap-2 ${collapsed ? "flex-col" : ""}`}>
          <button
            type="button"
            className="flex flex-1 items-center justify-center gap-2 rounded-lg border border-[var(--border)] px-2 py-2 text-sm"
            onClick={toggleTheme}
            title={theme === "dark" ? "Light" : "Dark"}
          >
            {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
            {!collapsed ? <span>{theme === "dark" ? "Light" : "Dark"}</span> : null}
          </button>
          <button
            type="button"
            className="flex flex-1 items-center justify-center gap-2 rounded-lg border border-[var(--border)] px-2 py-2 text-sm"
            onClick={logout}
            title="Sign out"
          >
            <LogOut size={16} />
            {!collapsed ? <span>Sign out</span> : null}
          </button>
        </div>
      </div>
    </div>
  );
}
