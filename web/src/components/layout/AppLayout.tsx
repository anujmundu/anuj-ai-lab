import { Header } from "@/components/layout/Header";
import { Inspector } from "@/components/inspector/Inspector";
import { Sidebar } from "@/components/navigation/Sidebar";
import { Workspace } from "@/components/workspace/Workspace";
import { useUIStore } from "@/stores";

export default function AppLayout() {
    const sidebarOpen = useUIStore((state) => state.sidebarOpen);
    const toggleSidebar = useUIStore((state) => state.toggleSidebar);
    const inspectorOpen = useUIStore((state) => state.inspectorOpen);
    const toggleInspector = useUIStore((state) => state.toggleInspector);

    return (
        <div className="flex h-screen flex-col bg-slate-50 dark:bg-slate-950">
            <Header />

            <div className="flex min-h-0 flex-1 overflow-hidden relative">
                {/* Platform Engine Sidebar */}
                {sidebarOpen && (
                    <>
                        {/* Mobile & Tablet Drawer Backdrop */}
                        <div
                            onClick={toggleSidebar}
                            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"
                        />
                        <div className="fixed inset-y-0 left-0 z-50 w-72 max-w-[85vw] shadow-2xl lg:hidden flex flex-col bg-white dark:bg-slate-950">
                            <Sidebar />
                        </div>

                        {/* Desktop Docked Sidebar */}
                        <div className="hidden lg:flex transition-all duration-200 shrink-0">
                            <Sidebar />
                        </div>
                    </>
                )}

                <Workspace />

                {/* Telemetry & Execution Inspector */}
                {inspectorOpen && (
                    <>
                        {/* Mobile & Tablet Drawer Backdrop */}
                        <div
                            onClick={toggleInspector}
                            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 xl:hidden"
                        />
                        <div className="fixed inset-y-0 right-0 z-50 w-80 max-w-[85vw] shadow-2xl xl:hidden flex flex-col bg-white dark:bg-slate-950">
                            <Inspector />
                        </div>

                        {/* Desktop Docked Inspector */}
                        <div className="hidden xl:flex transition-all duration-200 shrink-0">
                            <Inspector />
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}