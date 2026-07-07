import { Brain } from "lucide-react";

export default function EmptyMemory() {
    return (
        <div className="flex flex-1 items-center justify-center rounded-xl border border-dashed p-12">
            <div className="text-center">
                <Brain className="mx-auto mb-4 h-12 w-12 text-muted-foreground" />

                <h3 className="text-xl font-semibold">
                    No memories yet
                </h3>

                <p className="mt-2 text-sm text-muted-foreground">
                    Create your first persistent memory.
                </p>
            </div>
        </div>
    );
}