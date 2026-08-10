import * as React from "react";
import { cn } from "@/lib/utils";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: boolean;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, error, ...props }, ref) => (
    <input
      ref={ref}
      className={cn(
        "h-10 w-full rounded-md border bg-surface px-3 text-body-sm text-text-primary placeholder:text-text-secondary transition-colors duration-fast focus:outline-none focus-visible:ring-2 focus-visible:ring-primary disabled:opacity-50 disabled:bg-surface-secondary",
        error ? "border-critical" : "border-border",
        className
      )}
      {...props}
    />
  )
);
Input.displayName = "Input";

export { Input };
