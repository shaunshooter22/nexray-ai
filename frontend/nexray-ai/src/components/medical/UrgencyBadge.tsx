import { cn } from "@/lib/utils";
import type { Urgency } from "@/types/medical";
import { CircleAlert, AlertTriangle, AlertOctagon, CheckCircle2 } from "lucide-react";

const CONFIG: Record<Urgency, { label: string; classes: string; icon: typeof CheckCircle2 }> = {
  routine: { label: "Routine", classes: "bg-success-bg text-success-foreground", icon: CheckCircle2 },
  moderate: { label: "Moderate", classes: "bg-info-bg text-info-foreground", icon: CircleAlert },
  urgent: { label: "Urgent", classes: "bg-warning-bg text-warning-foreground", icon: AlertTriangle },
  critical: { label: "Critical", classes: "bg-critical-bg text-critical-foreground", icon: AlertOctagon },
};

export function UrgencyBadge({ urgency, className }: { urgency: Urgency; className?: string }) {
  const { label, classes, icon: Icon } = CONFIG[urgency];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-tiny font-medium",
        classes,
        className
      )}
    >
      <Icon size={12} />
      {label}
    </span>
  );
}
