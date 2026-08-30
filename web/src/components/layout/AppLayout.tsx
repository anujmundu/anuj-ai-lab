import { Header } from "@/components/layout/Header";
import { Inspector } from "@/components/inspector/Inspector";
import { Sidebar } from "@/components/navigation/Sidebar";
import { Workspace } from "@/components/workspace/Workspace";
import { useUIStore } from "@/stores";

export default function AppLayout() {
    const sidebarOpen = useUIStore((state) => state.sidebarOpen);
    const inspectorOpen = useUIStore((state) => state.inspectorOpen);

    return (
        <div className="flex h-screen flex-col bg-slate-50 dark:bg-slate-950">
            <Header />

            <div className="flex min-h-0 flex-1 overflow-hidden">
                {sidebarOpen && (
                    <div className="hidden lg:flex transition-all duration-200 shrink-0">
                        <Sidebar />
                    </div>
                )}

                <Workspace />

                {inspectorOpen && (
                    <div className="hidden xl:flex transition-all duration-200 shrink-0">
                        <Inspector />
                    </div>
                )}
            </div>
        </div>
    );
}