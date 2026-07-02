import { Header } from "@/components/layout/Header";
import { Inspector } from "@/components/inspector/Inspector";
import { Sidebar } from "@/components/navigation/Sidebar";
import { Workspace } from "@/components/workspace/Workspace";

export default function AppLayout() {
  return (
    <div className="flex h-screen flex-col bg-slate-50 dark:bg-slate-950">
      <Header />

      <div className="flex min-h-0 flex-1 overflow-hidden">
        <Sidebar />

        <Workspace />

        <Inspector />
      </div>
    </div>
  );
}