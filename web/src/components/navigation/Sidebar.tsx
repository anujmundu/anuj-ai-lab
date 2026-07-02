import {
  Brain,
  FileText,
  GitBranch,
  MessageSquare,
  Settings,
  Wrench,
} from "lucide-react";

import { ScrollArea } from "@/components/ui/scroll-area";

import { SidebarItem } from "./SidebarItem";

export function Sidebar() {
  return (
    <aside className="flex h-full w-64 flex-col border-r border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-950">
      <div className="border-b border-slate-200 px-4 py-4 dark:border-slate-800">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
          Navigation
        </h2>
      </div>

      <ScrollArea className="flex-1">
        <nav className="space-y-2 p-4">
          <SidebarItem
            icon={MessageSquare}
            label="Chat"
            active
          />

          <SidebarItem
            icon={FileText}
            label="Documents"
          />

          <SidebarItem
            icon={Brain}
            label="Memory"
          />

          <SidebarItem
            icon={Wrench}
            label="Tools"
          />

          <SidebarItem
            icon={GitBranch}
            label="Pipeline"
          />

          <SidebarItem
            icon={Settings}
            label="Settings"
          />
        </nav>
      </ScrollArea>

      <div className="border-t border-slate-200 p-4 dark:border-slate-800">
        <p className="text-xs text-slate-500">
          Anuj AI Lab
        </p>

        <p className="mt-1 text-xs text-slate-400">
          Modern AI Engineering Platform
        </p>
      </div>
    </aside>
  );
}