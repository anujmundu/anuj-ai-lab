import type { CitationInfo } from "@/types/diagnostics";

interface CitationCardProps {
    citations: CitationInfo;
}

export function CitationCard({
    citations,
}: CitationCardProps) {
    return (
        <div className="rounded-lg border bg-card p-4 shadow-sm">
            <h3 className="mb-4 text-sm font-medium text-muted-foreground">
                Citations
            </h3>

            <p className="leading-7">
                {citations.answer}
            </p>

            <div className="mt-6">
                <h4 className="mb-3 text-sm font-semibold">
                    Sources
                </h4>

                <div className="space-y-3">
                    {citations.source_mapping.map((source) => (
                        <div
                            key={source.chunk_id}
                            className="rounded-md border p-3"
                        >
                            <div className="font-medium">
                                {source.citation}
                            </div>

                            <div className="text-sm text-muted-foreground">
                                {source.filename}
                            </div>

                            <div className="text-xs text-muted-foreground">
                                Chunk {source.chunk_number} of{" "}
                                {source.total_chunks}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}