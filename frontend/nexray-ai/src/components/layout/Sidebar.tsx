import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  ScanLine,
  Stethoscope,
  ClipboardPlus,
  FileText,
  Settings,
  Activity,
  ChevronLeft,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useState } from "react";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/xray-analysis", label: "X-Ray Analysis", icon: ScanLine },
  { to: "/symptom-checker", label: "Symptom Checker", icon: Stethoscope },
  { to: "/new-case", label: "Combined Case", icon: ClipboardPlus },
  { to: "/reports", label: "Reports", icon: FileText },
  { to: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={cn(
        "hidden md:flex h-screen sticky top-0 flex-col border-r border-border bg-surface-secondary transition-all duration-default",
        collapsed ? "w-[76px]" : "w-[260px]"
      )}
    >
      {/* Brand */}
      <div className="flex items-center gap-3 px-5 h-16 border-b border-border">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-primary text-white">
          <Activity size={18} />
        </div>
        {!collapsed && (
          <div className="min-w-0">
            <p className="text-card-title leading-none text-text-primary truncate">NexRay AI</p>
            <p className="text-tiny text-text-secondary truncate">Clinical Assistant</p>
          </div>
        )}
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-4 px-3 flex flex-col gap-1">
        {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-md px-3 h-10 text-label transition-colors duration-fast",
                isActive
                  ? "bg-primary text-white"
                  : "text-text-secondary hover:bg-surface hover:text-text-primary"
              )
            }
          >
            <Icon size={18} className="shrink-0" />
            {!collapsed && <span className="truncate">{label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Collapse toggle */}
      <button
        onClick={() => setCollapsed((c) => !c)}
        className="flex items-center gap-2 mx-3 mb-4 h-9 px-3 rounded-md text-text-secondary hover:bg-surface hover:text-text-primary text-body-sm transition-colors duration-fast"
        aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
      >
        <ChevronLeft size={16} className={cn("transition-transform duration-default", collapsed && "rotate-180")} />
        {!collapsed && <span>Collapse</span>}
      </button>
    </aside>
  );
}