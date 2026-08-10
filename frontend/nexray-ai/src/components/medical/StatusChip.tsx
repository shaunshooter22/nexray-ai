import { cn } from "@/lib/utils";

type Status = "online" | "offline" | "processing";

const CONFIG: Record<Status, { label: string; dot: string; text: string }> = {
  online: { label: "Online", dot: "bg-accent", text: "text-success-foreground" },
  offline: { label: "Offline", dot: "bg-critical", text: "text-critical-foreground" },
  processing: { label: "Processing", dot: "bg-warning animate-pulse", text: "text-warning-foreground" },
};

export function StatusChip({ status, className }: { status: Status; className?: string }) {
  const { label, dot, text } = CONFIG[status];
  return (
    <span className={cn("inline-flex items-center gap-1.5 text-body-sm", text, className)}>
      <span className={cn("h-1.5 w-1.5 rounded-full", dot)} />
      {label}
    </span>
  );
}
