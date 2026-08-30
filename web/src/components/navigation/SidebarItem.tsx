import type { LucideIcon } from "lucide-react";
import { NavLink } from "react-router-dom";

import { cn } from "@/lib/utils";

type SidebarItemProps = {
    icon: LucideIcon;
    label: string;
    to: string;
    onNavigate?: () => void;
};

export function SidebarItem({
    icon: Icon,
    label,
    to,
    onNavigate,
}: SidebarItemProps) {
    return (
        <NavLink
            to={to}
            end={to === "/"}
            onClick={onNavigate}
            className={({ isActive }) =>
                cn(
                    "flex w-full items-center gap-3 rounded-xl px-3.5 py-2.5 text-xs font-medium transition-all",
                    isActive
                        ? "accent-bg font-semibold shadow-sm"
                        : "text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800/60 dark:hover:text-white",
                )
            }
        >
            <Icon className="h-4 w-4 shrink-0" />

            <span>{label}</span>
        </NavLink>
    );
}

export default SidebarItem;