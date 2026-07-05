import { Activity } from "lucide-react";

import { Card } from "@/components/ui/card";

export function Inspector() {
    return (
        <aside className="hidden h-full w-80 shrink-0 border-l border-slate-200 bg-white xl:flex xl:flex-col dark:border-slate-800 dark:bg-slate-950">
            <div className="border-b border-slate-200 px-5 py-4 dark:border-slate-800">
                <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
                    Inspector
                </h2>
            </div>

            <div className="flex-1 overflow-y-auto p-6">
                <Card className="border-dashed p-8">
                    <div className="flex flex-col items-center text-center">
                        <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-slate-100 dark:bg-slate-900">
                            <Activity className="h-7 w-7 text-slate-500" />
                        </div>

                        <h3 className="text-lg font-semibold">
                            No inspection available
                        </h3>

                        <p className="mt-2 text-sm text-slate-500">
                            Run a workflow or select a conversation to inspect
                            diagnostics, prompts, sources, and execution
                            details.
                        </p>
                    </div>
                </Card>
            </div>
        </aside>
    );
}

export default Inspector;