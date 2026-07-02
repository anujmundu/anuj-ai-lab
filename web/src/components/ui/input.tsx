import * as React from "react";

import { cn } from "@/lib/utils";

export type InputProps =
  React.InputHTMLAttributes<HTMLInputElement>;

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type = "text", ...props }, ref) => {
    return (
      <input
        ref={ref}
        type={type}
        className={cn(
          [
            "flex",
            "h-10",
            "w-full",
            "rounded-md",
            "border",
            "border-slate-300",
            "bg-white",
            "px-3",
            "py-2",
            "text-sm",
            "text-slate-900",
            "shadow-sm",
            "transition-colors",

            "placeholder:text-slate-500",

            "focus-visible:outline-none",
            "focus-visible:ring-2",
            "focus-visible:ring-slate-400",
            "focus-visible:ring-offset-2",

            "disabled:cursor-not-allowed",
            "disabled:opacity-50",

            "dark:border-slate-700",
            "dark:bg-slate-900",
            "dark:text-slate-100",
            "dark:placeholder:text-slate-400",
            "dark:focus-visible:ring-slate-500",

            "file:border-0",
            "file:bg-transparent",
            "file:text-sm",
            "file:font-medium",
            "file:text-slate-900",
            "dark:file:text-slate-100",
          ].join(" "),
          className
        )}
        {...props}
      />
    );
  }
);

Input.displayName = "Input";

export { Input };