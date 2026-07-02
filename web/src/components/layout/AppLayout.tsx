import { Header } from "@/components/layout/Header";
import { Sidebar } from "@/components/navigation/Sidebar";
import { Inspector } from "@/components/inspector/Inspector";
import { Workspace } from "@/components/workspace/Workspace";

export function AppLayout() {
  return (
    <div className="flex h-screen flex-col bg-slate-50 dark:bg-slate-950">
      <Header />

      <div className="flex min-h-0 flex-1">
        <Sidebar />

        <Workspace />

        <Inspector />
      </div>
    </div>
  );
}

export default AppLayout;