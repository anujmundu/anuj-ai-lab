import {
    Brain,
    FileText,
    Activity,
    MessageSquare,
    Settings,
    Wrench,
    Bot,
    Users,
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
                <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    AI Platform Engine
                </h2>
            </div>

            <ScrollArea className="flex-1">
                <nav className="space-y-1.5 p-3">
                    <SidebarItem
                        icon={MessageSquare}
                        label="AI Assistant"
                        to="/"
                        onNavigate={onNavigate}
                    />

                    <SidebarItem
                        icon={FileText}
                        label="Knowledge Base"
                        to="/documents"
                        onNavigate={onNavigate}
                    />

                    <SidebarItem
                        icon={Bot}
                        label="Autonomous Agents"
                        to="/agents"
                        onNavigate={onNavigate}
                    />

                    <SidebarItem
                        icon={Users}
                        label="Multi-Agent Debate"
                        to="/collaboration"
                        onNavigate={onNavigate}
                    />

                    <SidebarItem
                        icon={Brain}
                        label="Semantic Memory"
                        to="/memory"
                        onNavigate={onNavigate}
                    />

                    <SidebarItem
                        icon={Wrench}
                        label="Tools & Voice"
                        to="/tools"
                        onNavigate={onNavigate}
                    />

                    <SidebarItem
                        icon={Activity}
                        label="Telemetry & Pipeline"
                        to="/pipeline"
                        onNavigate={onNavigate}
                    />

                    <SidebarItem
                        icon={Settings}
                        label="Settings & Models"
                        to="/settings"
                        onNavigate={onNavigate}
                    />
                </nav>
            </ScrollArea>

            <div className="border-t border-slate-200 p-4 dark:border-slate-800">
                <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-slate-700 dark:text-slate-300">Anuj AI Lab</span>
                    <span className="text-slate-400 font-mono text-[10px]">v3.0.0</span>
                </div>
                <p className="mt-0.5 text-[11px] text-slate-400">
                    Local Enterprise AI Platform
                </p>
            </div>
        </>
    );
}

export default NavigationContent;