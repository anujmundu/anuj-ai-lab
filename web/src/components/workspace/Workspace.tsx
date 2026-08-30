import { Outlet } from "react-router-dom";

export function Workspace() {
    return (
        <main className="min-w-0 flex-1 overflow-y-auto bg-slate-50 dark:bg-slate-950">
            <div className="flex h-full w-full flex-col">
                <Outlet />
            </div>
        </main>
    );
}

export default Workspace;