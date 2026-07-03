export function EmptyChat() {
    return (
        <div className="flex flex-1 items-center justify-center rounded-xl border border-dashed p-10">
            <div className="text-center">
                <h2 className="text-xl font-semibold">
                    Start a conversation
                </h2>

                <p className="mt-3 text-sm text-muted-foreground">
                    Ask questions about your indexed
                    documents using Retrieval-Augmented
                    Generation.
                </p>
            </div>
        </div>
    );
}