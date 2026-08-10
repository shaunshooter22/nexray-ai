import { LogOut, ChevronDown } from "lucide-react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { logout, getDoctor } from "@/lib/api";

export function TopNav() {
  const navigate = useNavigate();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const doctor = getDoctor();

  const initials = doctor?.name
    ? doctor.name.split(" ").map((n: string) => n[0]).join("").slice(0, 2).toUpperCase()
    : "DR";

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <header className="sticky top-0 z-sticky flex h-16 items-center justify-end gap-4 border-b border-border bg-surface px-6">

      {/* Doctor identity + logout dropdown */}
      <div className="relative">
        <button
          className="flex items-center gap-3 rounded-md px-2 py-1 hover:bg-surface-secondary transition-colors"
          onClick={() => setDropdownOpen(!dropdownOpen)}
        >
          <div className="text-right hidden sm:block">
            <p className="text-body-sm font-medium text-text-primary leading-none">
              {doctor?.name ?? "Doctor"}
            </p>
            <p className="text-tiny text-text-secondary mt-0.5">
              {doctor?.email ?? ""}
            </p>
          </div>
          <Avatar>
            <AvatarFallback>{initials}</AvatarFallback>
          </Avatar>
          <ChevronDown size={14} className="text-text-secondary" />
        </button>

        {/* Dropdown menu */}
        {dropdownOpen && (
          <div className="absolute right-0 top-12 w-48 rounded-md border border-border bg-surface shadow-lg z-50">
            <button
              onClick={handleLogout}
              className="flex w-full items-center gap-2 px-4 py-3 text-body-sm text-text-primary hover:bg-surface-secondary transition-colors rounded-md"
            >
              <LogOut size={15} />
              Sign out
            </button>
          </div>
        )}
      </div>
    </header>
  );
}