export function LoadingMessage() {
    return (
        <div className="rounded-xl border bg-card p-4">
            <div className="text-xs font-semibold uppercase text-muted-foreground">
                Assistant
            </div>

            <p className="mt-3 animate-pulse">
                Thinking...
            </p>
        </div>
    );
}