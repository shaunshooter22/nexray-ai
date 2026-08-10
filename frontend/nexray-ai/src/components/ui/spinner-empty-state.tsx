import { Loader2, Inbox } from "lucide-react";
import { cn } from "@/lib/utils";
import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

export function Spinner({ className, size = 20 }: { className?: string; size?: number }) {
  return <Loader2 size={size} className={cn("animate-spin text-primary", className)} />;
}

interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description?: string;
  action?: ReactNode;
}

export function EmptyState({ icon: Icon = Inbox, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-surface-secondary text-text-secondary">
        <Icon size={22} />
      </div>
      <div>
        <p className="text-card-title text-text-primary">{title}</p>
        {description && <p className="text-body-sm text-text-secondary mt-1 max-w-sm">{description}</p>}
      </div>
      {action}
    </div>
  );
}
