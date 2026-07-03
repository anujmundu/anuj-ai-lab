import type { ChatSource } from "@/types";

interface SourceListProps {
    sources: ChatSource[];
}

export function SourceList({
    sources,
}: SourceListProps) {
    return (
        <div className="rounded-lg border bg-background p-4">
            <h3 className="mb-3 text-sm font-semibold">
                Sources
            </h3>

            <div className="space-y-2">
                {sources.map((source) => (
                    <div
                        key={source.chunk_id}
                        className="rounded border p-3 text-sm"
                    >
                        <div className="font-medium">
                            {source.filename}
                        </div>

                        <div className="text-muted-foreground">
                            Chunk {source.chunk_number} of{" "}
                            {source.total_chunks}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}