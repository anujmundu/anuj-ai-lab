import { NavigationContent } from "./NavigationContent";

export function Sidebar() {
    return (
        <aside className="flex h-full w-64 shrink-0 flex-col border-r border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-950">
            <NavigationContent />
        </aside>
    );
}

export default Sidebar;