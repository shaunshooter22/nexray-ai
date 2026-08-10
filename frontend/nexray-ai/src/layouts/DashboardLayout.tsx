import { Outlet, NavLink } from "react-router-dom";
import { Sidebar } from "@/components/layout/Sidebar";
import { TopNav } from "@/components/layout/TopNav";
import {
  LayoutDashboard,
  ScanLine,
  Stethoscope,
  ClipboardPlus,
  FileText,
  Settings,
} from "lucide-react";
import { cn } from "@/lib/utils";

const MOBILE_NAV = [
  { to: "/dashboard", label: "Home", icon: LayoutDashboard },
  { to: "/xray-analysis", label: "X-Ray", icon: ScanLine },
  { to: "/symptom-checker", label: "Symptoms", icon: Stethoscope },
  { to: "/new-case", label: "Combined", icon: ClipboardPlus },
  { to: "/reports", label: "Reports", icon: FileText },
  { to: "/settings", label: "Settings", icon: Settings },
];

export function DashboardLayout() {
  return (
    <div className="flex min-h-screen bg-background">
      {/* Sidebar — desktop only */}
      <Sidebar />

      <div className="flex-1 flex flex-col min-w-0">
        <TopNav />

        {/* Main content — add bottom padding on mobile for nav bar */}
        <main className="flex-1 p-4 md:p-8 pb-24 md:pb-8 animate-fade-in">
          <div className="mx-auto max-w-[1400px]">
            <Outlet />
          </div>
        </main>

        {/* Mobile bottom navigation — hidden on desktop */}
        <nav className="fixed bottom-0 left-0 right-0 z-50 flex md:hidden border-t border-border bg-surface">
          {MOBILE_NAV.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                cn(
                  "flex flex-1 flex-col items-center justify-center gap-0.5 py-2 text-center transition-colors",
                  isActive
                    ? "text-primary"
                    : "text-text-secondary hover:text-text-primary"
                )
              }
            >
              <Icon size={20} />
              <span className="text-[10px] leading-none">{label}</span>
            </NavLink>
          ))}
        </nav>
      </div>
    </div>
  );
}