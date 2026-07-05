import { Outlet } from "react-router-dom";

export function Workspace() {
    return (
        <main className="min-w-0 flex-1 overflow-y-auto bg-slate-50 dark:bg-slate-950">
            <div className="mx-auto flex h-full w-full max-w-screen-2xl flex-col">
                <Outlet />
            </div>
        </main>
    );
}

export default Workspace;