import { cn } from "@/lib/utils";

function colorFor(confidence: number) {
  if (confidence >= 80) return "bg-accent";
  if (confidence >= 50) return "bg-warning";
  return "bg-critical";
}

export function ConfidenceMeter({
  confidence,
  label = "AI confidence",
  className,
}: {
  confidence: number;
  label?: string;
  className?: string;
}) {
  return (
    <div className={cn("flex flex-col gap-1.5", className)}>
      <div className="flex items-center justify-between text-tiny text-text-secondary">
        <span>{label}</span>
        <span className="font-medium text-text-primary">{confidence}%</span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-surface-secondary">
        <div
          className={cn("h-full rounded-full transition-all duration-slow", colorFor(confidence))}
          style={{ width: `${confidence}%` }}
        />
      </div>
    </div>
  );
}
