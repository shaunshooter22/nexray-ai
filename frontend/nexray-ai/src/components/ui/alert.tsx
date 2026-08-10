import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { Info, CheckCircle2, AlertTriangle, AlertOctagon } from "lucide-react";
import { cn } from "@/lib/utils";

const alertVariants = cva("flex gap-3 rounded-md border p-4 text-body-sm", {
  variants: {
    variant: {
      info: "bg-info-bg border-info/20 text-info-foreground",
      success: "bg-success-bg border-success/20 text-success-foreground",
      warning: "bg-warning-bg border-warning/20 text-warning-foreground",
      critical: "bg-critical-bg border-critical/20 text-critical-foreground",
      neutral: "bg-surface-secondary border-border text-text-primary",
    },
  },
  defaultVariants: { variant: "info" },
});

const ICONS = {
  info: Info,
  success: CheckCircle2,
  warning: AlertTriangle,
  critical: AlertOctagon,
  neutral: Info,
};

export interface AlertProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof alertVariants> {
  title?: string;
}

function Alert({ className, variant = "info", title, children, ...props }: AlertProps) {
  const Icon = ICONS[variant ?? "info"];
  return (
    <div className={cn(alertVariants({ variant }), className)} {...props}>
      <Icon size={18} className="shrink-0 mt-0.5" />
      <div>
        {title && <p className="font-medium mb-0.5">{title}</p>}
        <div className="opacity-90">{children}</div>
      </div>
    </div>
  );
}

export { Alert };
