import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const badgeVariants = cva(
  [
    "inline-flex items-center rounded-full",
    "border px-2.5 py-0.5",
    "text-xs font-semibold",
    "transition-colors",
    "focus:outline-none",
    "focus:ring-2",
    "focus:ring-slate-400",
    "select-none",
  ].join(" "),
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-slate-900 text-white dark:bg-slate-100 dark:text-slate-900",

        secondary:
          "border-transparent bg-slate-100 text-slate-900 dark:bg-slate-800 dark:text-slate-100",

        outline:
          "border-slate-300 text-slate-700 dark:border-slate-700 dark:text-slate-300",

        success:
          "border-transparent bg-emerald-600 text-white",

        warning:
          "border-transparent bg-amber-500 text-white",

        destructive:
          "border-transparent bg-red-600 text-white",

        info:
          "border-transparent bg-sky-600 text-white",
      },
    },

    defaultVariants: {
      variant: "default",
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({
  className,
  variant,
  ...props
}: BadgeProps) {
  return (
    <div
      className={cn(
        badgeVariants({ variant }),
        className
      )}
      {...props}
    />
  );
}