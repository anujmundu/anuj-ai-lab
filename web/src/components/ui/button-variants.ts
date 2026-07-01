import { cva } from "class-variance-authority";

export const buttonVariants = cva(
  [
    "inline-flex items-center justify-center gap-2",
    "rounded-md",
    "text-sm font-medium",
    "whitespace-nowrap",
    "transition-colors duration-200",
    "focus-visible:outline-none",
    "focus-visible:ring-2",
    "focus-visible:ring-slate-400",
    "focus-visible:ring-offset-2",
    "ring-offset-background",
    "disabled:pointer-events-none",
    "disabled:opacity-50",
    "select-none",
    "[&_svg]:pointer-events-none",
    "[&_svg]:h-4",
    "[&_svg]:w-4",
    "[&_svg]:shrink-0",
  ].join(" "),
  {
    variants: {
      variant: {
        default: [
          "bg-slate-900",
          "text-white",
          "hover:bg-slate-800",
          "dark:bg-slate-100",
          "dark:text-slate-900",
          "dark:hover:bg-slate-200",
        ].join(" "),

        secondary: [
          "bg-slate-100",
          "text-slate-900",
          "hover:bg-slate-200",
          "dark:bg-slate-800",
          "dark:text-slate-100",
          "dark:hover:bg-slate-700",
        ].join(" "),

        outline: [
          "border",
          "border-slate-300",
          "bg-white",
          "hover:bg-slate-100",
          "dark:border-slate-700",
          "dark:bg-slate-900",
          "dark:hover:bg-slate-800",
        ].join(" "),

        ghost: [
          "hover:bg-slate-100",
          "dark:hover:bg-slate-800",
        ].join(" "),

        destructive: [
          "bg-red-600",
          "text-white",
          "hover:bg-red-700",
        ].join(" "),

        link: [
          "text-blue-600",
          "underline-offset-4",
          "hover:underline",
          "dark:text-blue-400",
        ].join(" "),
      },

      size: {
        sm: "h-8 px-3",

        default: "h-10 px-4 py-2",

        lg: "h-11 px-8",

        icon: "h-10 w-10 p-0",
      },
    },

    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);