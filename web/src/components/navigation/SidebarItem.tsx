import type { LucideIcon } from "lucide-react";

import { cn } from "@/lib/utils";

type SidebarItemProps = {
  icon: LucideIcon;
  label: string;
  active?: boolean;
};

export function SidebarItem({
  icon: Icon,
  label,
  active = false,
}: SidebarItemProps) {
  return (
    <button
      type="button"
      className={cn(
        "flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
        active
          ? "bg-slate-900 text-white dark:bg-white dark:text-slate-900"
          : "text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-white"
      )}
    >
      <Icon className="h-5 w-5 shrink-0" />

      <span>{label}</span>
    </button>
  );
}