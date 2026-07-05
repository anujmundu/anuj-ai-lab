import {
    Brain,
    FileText,
    GitBranch,
    MessageSquare,
    Settings,
    Wrench,
} from "lucide-react";

import { ScrollArea } from "@/components/ui/scroll-area";

import SidebarItem from "./SidebarItem";

interface NavigationContentProps {
    onNavigate?: () => void;
}

export function NavigationContent({
    onNavigate,
}: NavigationContentProps) {
    return (
        <>
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
                        to="/"
                        onNavigate={onNavigate}
                    />

                    <SidebarItem
                        icon={FileText}
                        label="Documents"
                        to="/documents"
                        onNavigate={onNavigate}
                    />

                    <SidebarItem
                        icon={Brain}
                        label="Memory"
                        to="/memory"
                        onNavigate={onNavigate}
                    />

                    <SidebarItem
                        icon={Wrench}
                        label="Tools"
                        to="/tools"
                        onNavigate={onNavigate}
                    />

                    <SidebarItem
                        icon={GitBranch}
                        label="Pipeline"
                        to="/pipeline"
                        onNavigate={onNavigate}
                    />

                    <SidebarItem
                        icon={Settings}
                        label="Settings"
                        to="/settings"
                        onNavigate={onNavigate}
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
        </>
    );
}

export default NavigationContent;